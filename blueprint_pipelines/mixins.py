from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_codestarconnections as codestarconnections,
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
        if (
            not hasattr(self, "codestar_connection_arn")
            or not self.codestar_connection_arn
        ):
            codestar_connection = codestarconnections.CfnConnection(
                self,
                connection_name,
                connection_name=connection_name,
                provider_type="GitHub",
            )
            self.codestar_connection_arn = codestar_connection.get_att(
                "ConnectionArn"
            ).to_string()

        # Define the artifacts that represent source code and cloud assembly.
        pipeline_source_artifact = codepipeline.Artifact()
        pipeline_cloud_assembly_artifact = codepipeline.Artifact()

        pipeline_source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=self.codestar_connection_arn,
            output=pipeline_source_artifact,
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
            source_artifact=pipeline_source_artifact,  # Where to get source code to build
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact,  # Where to place built source
            role_policy_statements=additional_synth_iam_statements,
            environment={"privileged": privileged},
        )

        # Create the pipeline.
        self.pipeline = pipelines.CdkPipeline(
            self,
            "Pipeline",
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact,
            source_action=pipeline_source_action,
            synth_action=pipeline_synth_action,
        )
