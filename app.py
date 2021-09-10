#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from controls_pipeline.controls_pipeline_stack import ControlsPipelineStack

app = cdk.App()

# Input parameters. Update according to your github owner and repo.
github_owner = "showley-vr"
controls_repo = "ControlsFoundation-ControlsPipeline"
application_repo = "ControlsFoundation-ApplicationPipeline"

ControlsPipelineStack(app, "ControlsPipeline", github_owner, controls_repo)
ControlsPipelineStack(app, "ApplicationPipeline", github_owner, application_repo)

app.synth()