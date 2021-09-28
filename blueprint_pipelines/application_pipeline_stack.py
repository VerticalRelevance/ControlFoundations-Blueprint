import logging
import os
from pathlib import Path

import jsii
from aws_cdk import (
    aws_codepipeline,
    core as cdk,
    aws_s3,
    aws_codepipeline_actions,
    aws_codebuild,
)

from mixins import PipelineMixin

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPLEMENTARY_FILES_DIR = os.path.join(CURRENT_DIR, "../supplementary_files")
REPO_OPA_BINARY_PATH = (
    "blueprint_pipelines/controls_scripts/lambdas/control_broker_opa_layer/bin/opa"
)
REPO_OPA_EVAL_SCRIPT_PATH = "blueprint_pipelines/controls_scripts/opa_eval.py"
REPO_OPA_CFN_TEMPL_OPA_POLICIES_DIR = (
    "blueprint_pipelines/controls_scripts/cfn_template_opa_policies"
)

logger = logging.getLogger(__name__)


@jsii.implements(cdk.IAspect)
class S3BucketPublicAccessOffAspect:
    def visit(self, node):
        if isinstance(node, aws_s3.Bucket):
            node._disallow_public_access = True


class ApplicationPipelineStack(cdk.Stack, PipelineMixin):
    """Deploy a pipeline that runs controls against the application CDK code before deploying it."""

    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        pipeline_repo_owner: str,
        pipeline_repo_name: str,
        application_repo_owner: str,
        application_repo_name: str,
        application_repo_branch: str = "main",
        pipeline_repo_branch: str = "main",
        codestar_connection_arn: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.github_repo_owner = pipeline_repo_owner
        self.github_repo_name = pipeline_repo_name
        self.github_repo_branch = pipeline_repo_branch
        self.application_repo_owner = application_repo_owner
        self.application_repo_name = application_repo_name
        self.application_repo_branch = application_repo_branch
        self.codestar_connection_arn = codestar_connection_arn

        self.configure_pipeline()

        # Turn off public access on any buckets created in this stack
        cdk.Aspects.of(self).add(S3BucketPublicAccessOffAspect())

    def configure_pipeline(self, *args, **kwargs):
        super().configure_pipeline(*args, **kwargs)
        self.application_source_artifact = aws_codepipeline.Artifact()
        application_source_action = (
            aws_codepipeline_actions.CodeStarConnectionsSourceAction(
                action_name="Application_GitHub_Source",
                connection_arn=self.codestar_connection_arn,
                output=self.application_source_artifact,
                owner=self.application_repo_owner,
                repo=self.application_repo_name,
                branch=self.application_repo_branch,
            )
        )
        self.pipeline_source_stage = self.pipeline.stage("Source")
        self.pipeline_source_stage.add_action(application_source_action)
        self.application_build_stage = self.pipeline.add_stage("BuildApplication")
        self.configure_application_build_stage()
        self.automated_controls_stage = self.pipeline.add_stage("RunAutomatedControls")
        self.configure_opa_check_stage()
        self.application_deploy_stage = self.pipeline.add_stage("DeployApplication")
        self.configure_application_deploy_stage()

    def configure_application_build_stage(self):
        self.application_cloud_assembly_artifact = aws_codepipeline.Artifact()
        self.application_build_codebuild_project = aws_codebuild.Project(
            self,
            "ApplicationBuild",
            build_spec=aws_codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "install": {
                            "runtime-versions": {"python": 3.8, "nodejs": 14},
                            "commands": [
                                "npm install -g aws-cdk",
                                "pip install --upgrade pip",
                                "pip install -r requirements.txt",
                            ],
                        },
                        "build": {
                            "commands": ["cdk synth"],
                        },
                    },
                    "artifacts": {"files": ["cdk.out/**"]},
                }
            ),
        )
        self.application_build_stage.add_actions(
            aws_codepipeline_actions.CodeBuildAction(
                input=self.application_source_artifact,
                outputs=[self.application_cloud_assembly_artifact],
                type=aws_codepipeline_actions.CodeBuildActionType.BUILD,
                run_order=self.application_build_stage.next_sequential_run_order(),
                project=self.application_build_codebuild_project,
                action_name="CdkSynth",
            )
        )

    def configure_application_deploy_stage(self):
        self.application_deploy_codebuild_project = aws_codebuild.Project(
            self,
            "ApplicationDeployment",
            build_spec=aws_codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "install": {
                            "runtime-versions": {"python": 3.8, "nodejs": 14},
                            "commands": [
                                "npm install -g aws-cdk",
                                "pip install --upgrade pip",
                                "pip install -r requirements.txt",
                            ],
                        },
                        "build": {
                            "commands": ["cdk deploy --all --require-approval never"],
                        },
                    },
                }
            ),
            role=self.self_mutate_codebuild_deploy_role,
        )
        self.application_deploy_stage.add_actions(
            aws_codepipeline_actions.CodeBuildAction(
                input=self.application_source_artifact,
                type=aws_codepipeline_actions.CodeBuildActionType.BUILD,
                run_order=self.application_deploy_stage.next_sequential_run_order(),
                project=self.application_deploy_codebuild_project,
                role=self.self_mutate_pipeline_action_role,
                action_name="AppDeploy",
            )
        )

    def configure_opa_check_stage(self):
        self.opa_codebuild_project = aws_codebuild.Project(
            self,
            "OpaIacCheck",
            build_spec=aws_codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "env": {"variables": {"OPA_BINARY_PATH": REPO_OPA_BINARY_PATH}},
                    "phases": {
                        "install": {
                            "runtime-versions": {"python": 3.7},
                            "commands": ["python --version"],
                        },
                        "build": {
                            "commands": [
                                "ls -alh .",
                                "ls -alh $CODEBUILD_SRC_DIR_source2",
                                "ls -alh $CODEBUILD_SRC_DIR_Artifact_BuildApplication_CdkSynth",
                                "env",
                                f"{REPO_OPA_EVAL_SCRIPT_PATH} {REPO_OPA_CFN_TEMPL_OPA_POLICIES_DIR} $CODEBUILD_SRC_DIR_Artifact_BuildApplication_CdkSynth/cdk.out/*.template.json",
                            ],
                        },
                    },
                }
            ),
        )
        self.automated_controls_stage.add_actions(
            aws_codepipeline_actions.CodeBuildAction(
                input=self.pipeline_source_artifact,
                extra_inputs=[self.application_cloud_assembly_artifact],
                type=aws_codepipeline_actions.CodeBuildActionType.BUILD,
                run_order=self.automated_controls_stage.next_sequential_run_order(),
                project=self.opa_codebuild_project,
                action_name="OPACheck",
            )
        )
