#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from blueprint_pipelines.controls_pipeline_stack import ControlsPipelineStack
from blueprint_pipelines.application_pipeline_stack import ApplicationPipelineStack

CONTROLS_PIPELINE_NAME = "ControlsFoundationControlsPipeline"
APPLICATION_PIPELINE_NAME = "ControlsFoundationApplicationPipeline"

app = cdk.App()

common_env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION"),
)

# Input parameters. Update according to your existing github owner name and repo names.
github_owner = "VerticalRelevance"
controls_repo = "ControlFoundations-Blueprint"
application_repo = "ControlFoundations-ExampleApp"
codestar_connection_arn_secret_id = "VRCodeStarConnectionLabConnectionArn"

# Allows us to detect whether we are running from within a pipeline's synth
# stage (like within the control pipeline's synth stage) or not (such as when
# first deploying). This helps us skip building the construct for a pipeline we
# are not executing, since (for instance) the application pipeline doesn't have
# permission to do things that the controls pipeline does, so trying to build
# the controls pipeline from within the application pipeline would fail.
currently_executing_pipeline = app.node.try_get_context("fromPipelineSynthStage")

if (
    not currently_executing_pipeline
    or currently_executing_pipeline == CONTROLS_PIPELINE_NAME
):
    ControlsPipelineStack(
        app,
        CONTROLS_PIPELINE_NAME,
        github_owner,
        controls_repo,
        codestar_connection_arn_secret_id=codestar_connection_arn_secret_id,
        env=common_env,
    )

if (
    not currently_executing_pipeline
    or currently_executing_pipeline == APPLICATION_PIPELINE_NAME
):
    ApplicationPipelineStack(
        app,
        APPLICATION_PIPELINE_NAME,
        github_owner,
        controls_repo,
        application_repo_owner=github_owner,
        application_repo_name=application_repo,
        codestar_connection_arn_secret_id=codestar_connection_arn_secret_id,
        env=common_env,
    )

app.synth()