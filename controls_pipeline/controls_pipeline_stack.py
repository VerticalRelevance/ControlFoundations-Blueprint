import logging
import os

import boto3
import jsii
from aws_cdk import (
    core as cdk,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_codestarconnections as codestarconnections,
    aws_s3,
    aws_s3_assets,
    aws_lambda,
    aws_config,
    aws_guardduty,
    aws_macie,
    aws_iam,
    aws_accessanalyzer,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPLEMENTARY_FILES_DIR = os.path.join(CURRENT_DIR, "../supplementary_files")
DEFAULT_CONFORMANCE_PACK_FILE_PATH = os.path.join(
    SUPPLEMENTARY_FILES_DIR, "s3-guardrails-conformance-pack.yaml"
)
DEFAULT_GUARDDUTY_THREAT_INTEL_SCRIPT_PATH = os.path.join(
    SUPPLEMENTARY_FILES_DIR, "threat-intel-my-ip.txt"
)

logger = logging.getLogger(__name__)


@jsii.implements(cdk.IAspect)
class S3BucketPublicAccessOffAspect:
    def visit(self, node):
        if isinstance(node, aws_s3.Bucket):
            node._disallow_public_access = True


class ControlsPipelineStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id: str,
        github_repo_owner: str,
        github_repo_name: str,
        local_guardduty_threat_intel_set_path: str = DEFAULT_GUARDDUTY_THREAT_INTEL_SCRIPT_PATH,
        local_conformance_pack_path: str = DEFAULT_CONFORMANCE_PACK_FILE_PATH,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.github_repo_owner = github_repo_owner
        self.github_repo_name = github_repo_name
        self.local_guardduty_threat_intel_set_path = (
            local_guardduty_threat_intel_set_path
        )
        self.local_conformance_pack_path = local_conformance_pack_path

        self.configure_utility_s3_bucket()
        self.configure_pipeline()

        self.configure_config_conformance_pack()
        self.configure_config_custom_rules()
        self.configure_guardduty()
        self.configure_iam_access_analyzer()
        self.configure_macie()

        # Turn off public access on any buckets created in this stack
        cdk.Aspects.of(self).add(S3BucketPublicAccessOffAspect())

    def configure_pipeline(self):
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
        # Policy for deploying the cfn template from the pipeline.
        
        self.pipeline_synth_stage_policy = aws_iam.PolicyStatement(
            # effect=aws_iam.Effect("ALLOW") --> default is allow
            actions=[
                "access-analyzer:ListAnalyzers",
                "macie2:GetMacieSession",
                "guardduty:ListDetectors"
            ],
            resources=["*"]
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
            role_policy_statements=[self.pipeline_synth_stage_policy],
        )

        # Create the pipeline.
        self.pipeline = pipelines.CdkPipeline(
            self,
            "Pipeline",
            cloud_assembly_artifact=pipeline_cloud_assembly_artifact,
            source_action=pipeline_source_action,
            synth_action=pipeline_synth_action,
        )

        #self.pipeline.add_stage(
            
        #)

    def configure_utility_s3_bucket(self):
        """Create an S3 bucket to store various stack assets in.

        Prevents us from creating tons of buckets for this one stack."""
        self.utility_s3_bucket = aws_s3.Bucket(
            self, "UtilityS3Bucket", bucket_name="controls-blueprint-utility-bucket-did-this-work"
        )

    def configure_config_conformance_pack(
        self,
    ):
        self.conformance_pack_asset = aws_s3_assets.Asset(
            self, "ConformancePackAsset", path=self.local_conformance_pack_path
        )

        self.config_conformance_pack = aws_config.CfnConformancePack(
            self,
            "Controls Foundation Test Pack",
            conformance_pack_name="s3-guardrails-conformance-pack",
            template_s3_uri=self.conformance_pack_asset.s3_object_url,
        )

    def configure_config_custom_rules(self):
        # Create lambda for custom config rule (detective).
        self.config_detective_rule_lambda = aws_lambda.Function(
            self,
            "Config-Rule-Detective",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("controls_pipeline/controls_scripts/lambdas"),
            handler="config_custom_rule_detective.handler",
        )
        # Create lambda for custom config rule (reactive).
        self.config_reactive_rule_lambda = aws_lambda.Function(
            self,
            "Config-Rule-Reactive",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset("controls_pipeline/controls_scripts/lambdas"),
            handler="config_custom_rule_reactive.handler",
        )

        # Create custom config rule (detective).
        self.config_detective_rule_scope = aws_config.RuleScope.from_tag(
            key="TEST-EC2_CUSTOM-CONFIG-RULE"
        )
        self.config_detective_rule = aws_config.CustomRule(
            self,
            "Detect EC2 Tag Violation",
            description="Detect when EC2 instances do not have an 'sdlc_env' tag attached",
            config_rule_name="DetectEc2TagViolation",
            lambda_function=self.config_detective_rule_lambda,
            rule_scope=self.config_detective_rule_scope,
            configuration_changes=True,
            periodic=True,
        )

        # Create custom config rule (detective).
        self.config_reactive_rule_scope = aws_config.RuleScope.from_tag(
            key="TEST-EC2_CUSTOM-CONFIG-RULE"
        )
        self.config_reactive_rule = aws_config.CustomRule(
            self,
            "React to EC2 Tag Violation",
            description="React to when EC2 instances do not have an 'sdlc_env' tag attached",
            config_rule_name="ReactToEc2TagViolation",
            lambda_function=self.config_reactive_rule_lambda,
            configuration_changes=True,
            periodic=True,
        )

    def configure_guardduty(self):
        # Create GuardDuty findings bucket.
        self.guardduty_findings_bucket = aws_s3.Bucket(
            self, "Controls-Foundation-GuardDuty-Findings"
        )
        # Create GuardDuty threat-intel-scripts bucket.
        self.guardduty_findings_bucket = aws_s3.Bucket(
            self, "Controls-Foundation-GuardDuty-Threat-Intel-Scripts"
        )

        # We cannot create multiple detectors in a single account/region
        guardduty_client = boto3.client("guardduty")
        if len(guardduty_client.list_detectors().get("DetectorIds", [None])) == 0:
            existing_detector_id = None
        else:
            existing_detector_id = guardduty_client.list_detectors().get(
                "DetectorIds", [None]
            )[0]
        if existing_detector_id is None:
            # Create account-level GuardDuty detector.
            self.guardduty_detector = aws_guardduty.CfnDetector(
                self,
                "Baseline GuardDuty Detector",
                enable=True,
                finding_publishing_frequency="ONE_HOUR",
            )
            existing_detector_id = self.guardduty_detector.ref

        self.guardduty_threat_intel_asset = aws_s3_assets.Asset(
            self,
            "GuardDutyThreatIntelAsset",
            path=self.local_guardduty_threat_intel_set_path,
        )

        self.guardduty_threat_intel_set = aws_guardduty.CfnThreatIntelSet(
            self,
            "My IP Threat Intel Set",
            activate=True,
            # Will either be a ref to the new detector or the pre-existing
            # detector ID
            detector_id=existing_detector_id,
            format="TXT",
            location=self.guardduty_threat_intel_asset.s3_object_url,
        )

    def configure_macie(self):
        macie_enabled = False

        macie_client = boto3.client("macie2")
        try:
            macie_enabled = macie_client.get_macie_session().get("status") == "ENABLED"
        except Exception as e:
            if "Macie is not enabled" not in str(e):
                raise

        if not macie_enabled:
            # Start Macie session
            self.macie_session = aws_macie.CfnSession(
                self,
                "Test Macie Session",
                finding_publishing_frequency="FIFTEEN_MINUTES",
                status="ENABLED",
            )

        self.macie_custom_data_identifier = aws_macie.CfnCustomDataIdentifier(
            self,
            "ControlsFoundationSSN",
            description="This is a Macie custom identifier that looks for PID data in S3 buckets.",
            name="controls-foundation-macie-test-pid",
            regex="(\d){3}-(\d){2}-(\d){4}",
        )

    def configure_iam_access_analyzer(self):
        access_analyzer_client = boto3.client("accessanalyzer")
        existing_analyzers = access_analyzer_client.list_analyzers().get(
            "analyzers", [{}]
        )
        active_analyzers = [
            analyzer
            for analyzer in existing_analyzers
            if analyzer.get("status") == "ACTIVE"
        ]
        if active_analyzers:
            logger.info(
                "Skipping creation of IAM access analyzer because an active instance already exists in the current account"
            )
        elif existing_analyzers and not active_analyzers:
            logger.warning(
                "Cannot create an Analyzer because at least one exists and none are in ACTIVE status"
            )
        else:
            # Create an account-level analyzer
            self.account_analyzer = aws_accessanalyzer.CfnAnalyzer(
                self, "Account IAM Access Analyzer", type="ACCOUNT"
            )
