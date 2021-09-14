#!/usr/bin/env python3
from controls_pipeline.controls_scripts.controls import *
import os

from aws_cdk import core as cdk

from controls_pipeline.controls_pipeline_stack import ControlsPipelineStack

app = cdk.App()

# Input parameters. Update according to your existing github owner name and repo names.
github_owner = "showley-vr"
controls_repo = "ControlsFoundation-ControlsPipeline"
application_repo = "ControlsFoundation-ApplicationPipeline"

# Initialize the stacks.
controls_stack = ControlsPipelineStack(app, "ControlsFoundationControlsPipeline", github_owner, controls_repo)
application_stack = ControlsPipelineStack(app, "ControlsFoundationTestApplicationPipeline", github_owner, application_repo)

# Create the pipelines.
controls_stack.deploy_pipeline()
application_stack.deploy_pipeline()

# Deploy security controls.
controls_stack.deploy_controls()

app.synth()