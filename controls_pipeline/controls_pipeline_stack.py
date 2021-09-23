import logging
import os
from pathlib import Path

import jsii
from aws_cdk import (
    core as cdk,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_codestarconnections as codestarconnections,
    aws_s3,
    aws_s3_assets,
    aws_iam,
)

#from control_broker import ControlBroker

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPLEMENTARY_FILES_DIR = os.path.join(CURRENT_DIR, "../supplementary_files")

logger = logging.getLogger(__name__)


@jsii.implements(cdk.IAspect)
class S3BucketPublicAccessOffAspect:
    def visit(self, node):
        if isinstance(node, aws_s3.Bucket):
            node._disallow_public_access = True


class ControlsPipelineStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        github_repo_owner: str,
        github_repo_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.github_repo_owner = github_repo_owner
        self.github_repo_name = github_repo_name

        self.configure_pipeline()

        # Turn off public access on any buckets created in this stack
        cdk.Aspects.of(self).add(S3BucketPublicAccessOffAspect())

    def configure_pipeline(self):
        # Create codestar connection to connect pipeline to git.
        connection_name = "".join(
            (
                # The connector name is concatenated here because the max_length of the connection_name attribute is 32.
                self.github_repo_name[19 : len(self.github_repo_name) - 2],
                "_git_connection",
            )
        )
        pipeline_git_connection = codestarconnections.CfnConnection(
            self,
            connection_name,
            connection_name=connection_name,
            provider_type="GitHub",
        )

        # Define the artifacts that represent source code and cloud assembly.
        pipeline_source_artifact = codepipeline.Artifact()
        pipeline_cloud_assembly_artifact = codepipeline.Artifact()

        # Define pipeline source action.
        git_connection_arn = pipeline_git_connection.get_att(
            "ConnectionArn"
        ).to_string()

        pipeline_source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=git_connection_arn,
            output=pipeline_source_artifact,
            owner=self.github_repo_owner,
            repo=self.github_repo_name,
        )
        
        self.pipeline_synth_stage_policy = aws_iam.PolicyStatement(
            # effect=aws_iam.Effect("ALLOW") --> default is allow
            actions=[
                "access-analyzer:ListAnalyzers",
                "macie2:GetMacieSession",
                "guardduty:ListDetectors"
            ],
            resources=["*"]
        )

        # Define pipeline synth action.
        pipeline_synth_action = pipelines.SimpleSynthAction(
            install_commands=[
                "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                "pip install --upgrade pip",
                "pip install -r requirements.txt",  # Instructs Codebuild to install required packages
            ],
            synth_command="npx cdk synth",
            source_artifact=pipeline_source_artifact,  # Where to get source code to build
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact,  # Where to place built source
            role_policy_statements=[self.pipeline_synth_stage_policy],
        )

        # Create the pipeline.
        self.pipeline = pipelines.CdkPipeline(
            self,
            "Pipeline",
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact,
            source_action=pipeline_source_action,
            synth_action=pipeline_synth_action,
        )