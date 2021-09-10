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

        connection_name = "".join((github_repo_name, "_git_connection"))
        git_connection = codestarconnections.CfnConnection(self, connection_name, connection_name="git_connection_props", provider_type="GitHub")
        git_connection_arn = git_connection.get_att("ConnectionArn").to_string()   
        # git_connection_arn = git_connection.connection_arn
#--------Initialize a codecommit repo if codecommit is the desired source control.--------#     
#        repo = codecommit.Repository(
#            self, repo_name,
#           repository_name=repo_name
#        )
#-----------------------------------------------------------------------------------------#

        # Defines the artifact representing the sourcecode
        source_artifact = codepipeline.Artifact()
        # Defines the artifact representing the cloud assembly
        # (cloudformation template + all other assets)
        cloud_assembly_artifact = codepipeline.Artifact()

        pipeline = pipelines.CdkPipeline(
            self, 'Pipeline',
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
                action_name="Github_Source",
                connection_arn=git_connection_arn,
                output=source_artifact,
                owner=github_repo_owner,
                repo=github_repo_name
            ),

            # Builds our source code outlined above into a could assembly artifact
            synth_action=pipelines.SimpleSynthAction(
                install_commands=[
                    'npm install -g aws-cdk', # Installs the cdk cli on Codebuild
                    'pip install -r requirements.txt' # Instructs Codebuild to install required packages
                ],
                synth_command='npx cdk synth',
                source_artifact=source_artifact, # Where to get source code to build
                cloud_assembly_artifact=cloud_assembly_artifact, # Where to place built source
            )
        )
