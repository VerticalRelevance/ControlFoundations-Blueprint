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
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        github_repo_owner: str,
        github_repo_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.github_repo_owner = github_repo_owner
        self.github_repo_name = github_repo_name

        self.configure_pipeline()

        # Turn off public access on any buckets created in this stack
        cdk.Aspects.of(self).add(S3BucketPublicAccessOffAspect())