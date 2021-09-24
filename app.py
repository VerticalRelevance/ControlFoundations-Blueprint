#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from controls_pipeline.controls_pipeline_stack import ControlsPipelineStack
from controls_pipeline.application_pipeline_stack import ApplicationPipelineStack

app = cdk.App()

common_env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"), region=os.environ.get("CDK_DEFAULT_REGION")
)

# Input parameters. Update according to your existing github owner name and repo names.
github_owner = "VerticalRelevance"
controls_repo = "ControlFoundations-Blueprint"
application_repo = "ControlFoundations-ExampleApp"
codestar_connection_arn = "***REMOVED***"

# Initialize the stacks.
controls_stack = ControlsPipelineStack(
    app,
    "ControlsFoundationControlsPipeline",
    github_owner,
    controls_repo,
    codestar_connection_arn=codestar_connection_arn,
    env=common_env
)

application_stack = ApplicationPipelineStack(
    app,
    "ControlsFoundationApplicationPipeline",
    github_owner,
    controls_repo,
    application_repo_owner=github_owner,
    application_repo_name=application_repo,
    codestar_connection_arn=codestar_connection_arn,
    env=common_env,
)

app.synth()