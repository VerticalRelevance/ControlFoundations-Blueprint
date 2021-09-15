import boto3

# Initialize Paraneters
ec2 = boto3.client("ec2", region_name="us-east-2")
config_client = boto3.client("config")
resources = ""

def handler(event, context):
    # Get the details of the resources that are not compliant with our detective custom config rule.
    details = config_client.get_compliance_details_by_config_rule(
        ConfigRuleName = "DetectEc2TagViolation", 
        ComplianceTypes = ["NON_COMPLIANT"]
    )
    # If the 
    if len(details["EvaluationResults"]) > 0:

        for result in details["EvaluationResults"]:
            print(result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]
                    ["ResourceId"])
            resources = resources + result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceId"] + "\n"
        
        resource_type = result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceType"]

        # If there is a non-compliant resourec and the non-compliant resource is an EC2 instance, stop the instance. 
        if (details == True) and (resource_type == "AWS::EC2::Instance"):
            instances = result["EvaluationResultIdentifier"]["EvaluationResultQualifier"]["ResourceId"]
            ec2.stop_instances(InstanceIds = instances)