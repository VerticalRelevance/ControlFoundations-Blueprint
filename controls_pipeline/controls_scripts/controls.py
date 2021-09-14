from aws_cdk import(
    aws_s3,
    aws_config,
    aws_guardduty,
    aws_macie,
    aws_accessanalyzer
)

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

def deploy_guardduty():
    # Insert guardduty construct call here.
    print("GuardDuty here.")

def deploy_macie(self):
    # Start Macie session
    session = aws_macie.CfnSession(self, "Test Macie Session", 
        finding_publishing_frequency = "FIFTEEN_MINUTES",
        status = "ENABLED")

    custom_data_identifier = aws_macie.CfnCustomDataIdentifier(self, "Controls Foundation Macie",
        description = "This is a Macie custom identifier that PID data in S3 buckets.",
        name = "controls-foundation-macie-test-pid",
        regex = "(\d){3}-(\d){2}-(\d){4}"
    )

def deploy_iam_access_analyzer():
    # Insert aim_access_analyzer construct call here.
    print("GuardDuty here.")