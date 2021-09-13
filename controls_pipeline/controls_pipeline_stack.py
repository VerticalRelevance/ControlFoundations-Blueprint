from aws_cdk import (
    core as cdk,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_codestarconnections as codestarconnections
)


class ControlsPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, github_repo_owner: str, github_repo_name: str, **kwargs) -> None:
        
        super().__init__(scope, id, **kwargs)

        # Create codestar connection to connect pipeline to git.
        connection_name = "".join((github_repo_name, "_git_connection"))
        pipeline_git_connection = codestarconnections.CfnConnection(self, connection_name, 
            connection_name="git_connection_props", 
            provider_type="GitHub"
        )   

        # Define the artifacts that represent source code and cloud assembly.
        pipeline_source_artifact = codepipeline.Artifact()
        pipeline_cloud_assembly_artifact = codepipeline.Artifact()

        # Define pipeline source action.
        git_connection_arn = pipeline_git_connection.get_att("ConnectionArn").to_string()
        pipeline_source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=git_connection_arn,
            output=pipeline_source_artifact,
            owner=github_repo_owner,
            repo=github_repo_name
        )

        # Define pipeline synth action.
        pipeline_synth_action = pipelines.SimpleSynthAction(
            install_commands=[
                'npm install -g aws-cdk', # Installs the cdk cli on Codebuild
                'pip install -r requirements.txt' # Instructs Codebuild to install required packages
            ],
            synth_command='npx cdk synth',
            source_artifact=pipeline_source_artifact, # Where to get source code to build
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact, # Where to place built source
        )

        # Create the pipeline.
        pipeline = pipelines.CdkPipeline(
            self, 'Pipeline',
            cloud_assembly_artifact = pipeline_cloud_assembly_artifact,
            source_action = pipeline_source_action,
            synth_action = pipeline_synth_action
        )
