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
github_owner = "showley-vr"
controls_repo = "ControlsFoundation-ControlsPipeline"
application_repo = "ControlsFoundation-ApplicationPipeline"

# Initialize the stacks.
controls_stack = ControlsPipelineStack(
    app,
    "ControlsFoundationControlsPipeline",
    github_owner,
    controls_repo,
    env=common_env
)

application_stack = ApplicationPipelineStack(
    app,
    "ControlsFoundationApplicationPipeline",
    github_owner,
    application_repo,
    env=common_env,
)

## Create the pipelines.
#controls_stack.configure_pipeline()
#application_stack.configure_pipeline()

## Deploy security controls.
#application_stack.configure_utility_s3_bucket()
#application_stack.configure_config_conformance_pack()
#application_stack.configure_config_custom_rules()
#application_stack.configure_guardduty()
#application_stack.configure_iam_access_analyzer()
#application_stack.configure_macie()

app.synth()