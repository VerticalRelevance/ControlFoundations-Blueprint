import boto3
from aws_cdk import (
    core as cdk,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codestarconnections as codestarconnections,
    aws_iam as iam,
    pipelines as pipelines,
)


class PipelineMixin:
    """Add to a stack class and call configure_pipeline inside its constructor to make a self-mutating pipeline out of it.

    Expects self.github_repo_name, self.github_repo_owner, and self.github_repo_branch to be defined.

    If you want to use an existing CodeStar connection for the source stage, specify its arn with
    self.codestar_connection_arn

    additional_synth_iam_statements are added to the synth stage role"""

    def configure_pipeline(
        self, additional_synth_iam_statements=None, privileged=False
    ):
        # Create codestar connection to connect pipeline to git.
        # The connector name is sliced here because the max length
        # of the connection_name attribute is 32.
        connection_name = self.github_repo_name[:32]
        self.codestar_connection_arn_secret_id = (
            self.codestar_connection_arn_secret_id
            if hasattr(self, "codestar_connection_arn_secret_id")
            else None
        )
        if self.codestar_connection_arn_secret_id:
            secrets_client = boto3.client("secretsmanager")
            self.codestar_connection_arn = secrets_client.get_secret_value(
                SecretId=self.codestar_connection_arn_secret_id
            )["SecretString"]
        else:
            codestar_connection = codestarconnections.CfnConnection(
                self,
                connection_name,
                connection_name=connection_name,
                provider_type="GitHub",
            )
            self.codestar_connection_arn = codestar_connection.get_att(
                "ConnectionArn"
            ).to_string()

        if self.codestar_connection_arn_secret_id:
            ssm_statement = iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "secretsmanager:SecretId": self.format_arn(
                            resource="secret",
                            service="secretsmanager",
                            resource_name=f"*{self.codestar_connection_arn_secret_id}*",
                            arn_format=cdk.ArnFormat.COLON_RESOURCE_NAME,
                        )
                    }
                },
            )
            if additional_synth_iam_statements is None:
                additional_synth_iam_statements = [ssm_statement]
            elif isinstance(additional_synth_iam_statements, list):
                additional_synth_iam_statements.append(ssm_statement)

        # Define the artifacts that represent source code and cloud assembly.
        self.pipeline_source_artifact = codepipeline.Artifact()
        self.pipeline_cloud_assembly_artifact = codepipeline.Artifact()

        pipeline_source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="Pipeline_GitHub_Source",
            connection_arn=self.codestar_connection_arn,
            output=self.pipeline_source_artifact,
            owner=self.github_repo_owner,
            repo=self.github_repo_name,
            branch=self.github_repo_branch,
        )

        # Define pipeline synth action.
        pipeline_synth_action = pipelines.SimpleSynthAction(
            install_commands=[
                "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                "pip install --upgrade pip",
                "pip install -r requirements.txt",  # Instructs Codebuild to install required packages
            ],
            synth_command=f"npx cdk synth -c 'fromPipelineSynthStage={self.stack_name}' {self.stack_name}",
            source_artifact=self.pipeline_source_artifact,  # Where to get source code to build
            cloud_assembly_artifact=self.pipeline_cloud_assembly_artifact,  # Where to place built source
            role_policy_statements=additional_synth_iam_statements,
            environment={"privileged": privileged},
        )

        # Create the pipeline.
        self.pipeline = pipelines.CdkPipeline(
            self,
            "Pipeline",
            cloud_assembly_artifact=self.pipeline_cloud_assembly_artifact,
            source_action=pipeline_source_action,
            synth_action=pipeline_synth_action,
        )

        self.self_mutate_pipeline_action_role = [
            r
            for r in self.pipeline.node.find_all()
            if r.node.path.endswith(
                "/Pipeline/Pipeline/UpdatePipeline/SelfMutate/CodePipelineActionRole"
            )
        ][0]
        self.self_mutate_codebuild_deploy_role = [
            r
            for r in self.pipeline.node.find_all()
            if r.node.path.endswith("/Pipeline/UpdatePipeline/SelfMutation/Role")
        ][0]
