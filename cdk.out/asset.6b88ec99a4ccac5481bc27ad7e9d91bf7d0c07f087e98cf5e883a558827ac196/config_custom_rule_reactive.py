import boto3

# Initialize Paraneters
ec2 = boto3.client("ec2", region_name="us-east-2")
config_client = boto3.client("config")
instanceIds = []

def handler(event, context):
    # Get the details of the resources that are not compliant with our detective custom config rule (DetectEc2TagViolation).
    details = config_client.get_compliance_details_by_config_rule(
        ConfigRuleName = "DetectEc2TagViolation", 
        ComplianceTypes = ["NON_COMPLIANT"]
    )
    # If there are non_compliant instances for our detective custom rule, stop the non_compliant instances.
    if len(details["EvaluationResults"]) != 0:
        # Compile a list of instance IDs of non_compliant instances.
        for detail in details["EvaluationResults"]:
            instanceIds.append(detail["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceId"])
        # For each non-compliant insta
        for instanceId in instanceIds:
            ec2.stop_instances(InstanceIds=instanceId)