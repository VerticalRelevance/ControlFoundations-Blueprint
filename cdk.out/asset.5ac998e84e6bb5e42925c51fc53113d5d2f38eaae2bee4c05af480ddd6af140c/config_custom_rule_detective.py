# Import packages.
import json
import boto3
 
 # Initalize parameters.
config = boto3.client("config")
compliance_value = "NOT_APPLICABLE"

def handler(event, context):
    
    # Parse the event argument for invokingEvent, ruleParameters, configurationItem, and configurationItemStatus.
    invoking_event = json.loads(event["invokingEvent"])
    rule_parameters = json.loads(event["ruleParameters"])
    item = invoking_event["configurationItem"]
    item_status = item["configurationItemStatus"]
    
    # Check if the event is eligible to be evaluated, and if so evaluate it.
    if eligible_event(item_status, event):
        compliance_value = evaluate_compliance(item, rule_parameters)

    # Send the rule evaluation back to config with put_evaluations().
    config.put_evaluations(
        Evaluations=[
            {
                "ComplianceResourceType": item["resourceType"],
                "ComplianceResourceId": item["resourceId"],
                "ComplianceType": compliance_value,
                "OrderingTimestamp": item["configurationItemCaptureTime"]
            },
        ],
        ResultToken=event["resultToken"])

# Check if the rule is eligible to be evaluated.
def eligible_event(item_status, event):
    event_left_scope = event["eventLeftScope"]
    if ((item_status == "OK") or (item_status == "ResourceDiscovered")) and event_left_scope is False:
        return True
    else:
        return False

# Evaluate based on the rule and return the compliance.
def evaluate_compliance(config_item, rule_parameters):
    if config_item["resourceType"] is "AWS::EC2::Instance":
        if len(config_item["configuration"]["tags"]) <= 1:
            return "NON_COMPLIANT"
        elif len(config_item["configuration"]["tags"]) > 1:
            return "COMPLIANT"
        else:    
            return "NOT_APPLICABLE"
    else:
        return "COMPLIANT"