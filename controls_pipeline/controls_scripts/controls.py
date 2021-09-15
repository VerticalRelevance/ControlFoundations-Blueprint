# Import aws_cdk packages.
from aws_cdk import(
    aws_s3,
    aws_lambda,
    aws_config,
    aws_guardduty,
    aws_macie,
    aws_accessanalyzer
)
# Import local lambda functions.
from controls_scripts.lambdas.config_custom_rule_detective import *
from controls_scripts.lambdas.config_custom_rule_reactive import *

def deploy_config_conformance_pack(self,
                                    conformance_pack_name="s3-guardrails-conformance-pack",
                                    conformance_pack_template_s3_uri="s3://controls-foundation-conformance-packs-personal/s3-guardrails-conformance-pack.yaml",
                                    s3_delivery_bucket_name="controls-foundation-config-conformance-bucket"):

    # Launch specified Config Conformance Pack.
    conformance_pack = aws_config.CfnConformancePack(self, "Controls Foundation Test Pack",
        conformance_pack_name=conformance_pack_name,
        #conformance_pack_input_parameters = None,
        delivery_s3_bucket=s3_delivery_bucket_name,
        template_s3_uri = conformance_pack_template_s3_uri
    )

def deploy_config_custom_rules(self):
    # Create lambda for custom config rule (detective).
    detective_config_rule_lambda = aws_lambda.Function(self, "Config-Rule-Detective", 
            runtime=aws_lambda.Runtime.PYTHON_3_7, 
            code= aws_lambda.Code.asset("controls_pipeline/controls_scripts/lambdas"), 
            handler="config_custom_rule_detective.handler"
    )
    # Create lambda for custom config rule (reactive).
    reactive_config_rule_lambda = aws_lambda.Function(self, "Config-Rule-Reactive", 
            runtime=aws_lambda.Runtime.PYTHON_3_7, 
            code= aws_lambda.Code.asset("controls_pipeline/controls_scripts/lambdas"), 
            handler="config_custom_rule_reactive.handler"
    )

    # Create custom config rule (detective).
    detective_config_rule_scope = aws_config.RuleScope.from_tag(key="TEST-EC2_CUSTOM-CONFIG-RULE")
    detective_config_rule = aws_config.CustomRule(self, "Detect EC2 Tag Violation",
        description = "Detect when EC2 instances do not have an 'sdlc_env' tag attached",
        config_rule_name = "DetectEc2TagViolation",
        lambda_function = detective_config_rule_lambda,
        rule_scope = detective_config_rule_scope,
        configuration_changes = True,
        periodic = True
    )

    # Create custom config rule (detective).
    reactive_config_rule_scope = aws_config.RuleScope.from_tag(key="TEST-EC2_CUSTOM-CONFIG-RULE")
    reactive_config_rule = aws_config.CustomRule(self, "React to EC2 Tag Violation",
        description = "React to when EC2 instances do not have an 'sdlc_env' tag attached",
        config_rule_name = "ReactToEc2TagViolation",
        lambda_function = reactive_config_rule_lambda,
        # rule_scope = reactive_config_rule_scope,
        configuration_changes = True,
        periodic = True
    )

def deploy_guardduty(self):
    # Create GuardDuty findings bucket.
    guardduty_findings_bucket = aws_s3.Bucket(self, "Controls-Foundation-GuardDuty-Findings", 
        bucket_name="controls-foundation-guardduty-findings"
    )
    # Create GuardDuty threat-intel-scripts bucket.
    guardduty_findings_bucket = aws_s3.Bucket(self, "Controls-Foundation-GuardDuty-Threat-Intel-Scripts", 
        bucket_name="controls-foundation-guardduty-threat-intel-scripts"
    )
    # Create account-level GuardDuty detector.
    guardduty_detector = aws_guardduty.CfnDetector(self, "Baseline GuardDuty Detector",
        enable = True,
        finding_publishing_frequency = "ONE_HOUR"
    )
    # Create GuardDuty threat intel list containing only my IP.
    threat_intel_script_uri = "s3://controls-foundation-guardduty-threat-intel-scripts/my_ip.txt"
    guardduty_detector_id = "40bdf400eb59b19eac1e41600ad9edb3"
    threat_intel_set = aws_guardduty.CfnThreatIntelSet(self, "My IP Threat Intel Set",
        activate = True,
        detector_id = guardduty_detector_id,
        format = "TXT",
        location = threat_intel_script_uri
    )

def deploy_macie(self):
    # Create GuardDuty findings bucket.
    macie_findings_bucket = aws_s3.Bucket(self, "Controls-Foundation-Macie-Findings", 
        bucket_name="controls-foundation-macie-findings"
    )
    # Start Macie session
    session = aws_macie.CfnSession(self, "Test Macie Session", 
        finding_publishing_frequency = "FIFTEEN_MINUTES",
        status = "ENABLED"
    )

    custom_data_identifier = aws_macie.CfnCustomDataIdentifier(self, "Controls Foundation Macie",
        description = "This is a Macie custom identifier that PID data in S3 buckets.",
        name = "controls-foundation-macie-test-pid",
        regex = "(\d){3}-(\d){2}-(\d){4}"
    )

def deploy_iam_access_analyzer(self):
    # Create an account-level analyzer
    account_analyzer = aws_accessanalyzer.CfnAnalyzer(self, "Account IAM Access Analyzer",
        type = "ACCOUNT"
)

