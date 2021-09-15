import boto3

# Initialize Paraneters
ec2 = boto3.client("ec2", region_name="us-east-2")
config_client = boto3.client("config")
non_compliant_resources = ""

def handler(event, context):
    non_compliance_detail = config_client.get_compliance_details_by_config_rule(
        ConfigRuleName = "DetectEc2TagViolation", 
        ComplianceTypes = ["NON_COMPLIANT"]
    )

    if len(non_compliance_detail["EvaluationResults"]) > 0:

        for result in non_compliance_detail["EvaluationResults"]:
            print(result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]
                    ["ResourceId"])
            non_compliant_resources = non_compliant_resources + result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceId"] + "\n"
        
        resource_type = result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceType"]

        if resource_type == "AWS::EC2::Instance" and non_compliance_detail:
            ec2.stop_instances(InstanceIds= result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceId"])