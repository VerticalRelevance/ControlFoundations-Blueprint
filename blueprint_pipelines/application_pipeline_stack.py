import logging
import os
from pathlib import Path

import jsii
from aws_cdk import (
    core as cdk,
    aws_s3,
)

from mixins import PipelineMixin

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPLEMENTARY_FILES_DIR = os.path.join(CURRENT_DIR, "../supplementary_files")

logger = logging.getLogger(__name__)


@jsii.implements(cdk.IAspect)
class S3BucketPublicAccessOffAspect:
    def visit(self, node):
        if isinstance(node, aws_s3.Bucket):
            node._disallow_public_access = True


class ApplicationPipelineStack(cdk.Stack, PipelineMixin):
    """Deploy a pipeline that runs controls against the application CDK code before deploying it."""

    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        pipeline_repo_owner: str,
        pipeline_repo_name: str,
        application_repo_owner: str,
        application_repo_name: str,
        application_repo_branch: str = "main",
        pipeline_repo_branch: str = "main",
        codestar_connection_arn: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.github_repo_owner = pipeline_repo_owner 
        self.github_repo_name = pipeline_repo_name
        self.github_repo_branch = pipeline_repo_branch
        self.application_repo_owner = application_repo_owner
        self.application_repo_name = application_repo_name
        self.application_repo_branch = application_repo_branch
        self.codestar_connection_arn = codestar_connection_arn

        self.configure_pipeline()

        # Turn off public access on any buckets created in this stack
        cdk.Aspects.of(self).add(S3BucketPublicAccessOffAspect())
