from aws_cdk import (
    core as cdk,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_codestarconnections as codestarconnections,
)

class PipelineMixin:
    """Add to a class and call configure_pipeline inside its constructor to make a self-mutating pipeline out of it.

    Expects self.github_repo_name and self.github_repo_owner to be defined.
    
    additional_synth_iam_statements are added to the synth stage role"""
    def configure_pipeline(self, additional_synth_iam_statements=None):
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
            role_policy_statements=additional_synth_iam_statements,
        )

        # Create the pipeline.
        self.pipeline = pipelines.CdkPipeline(
            self,
            "Pipeline",
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact,
            source_action=pipeline_source_action,
            synth_action=pipeline_synth_action,
        )