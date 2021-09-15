# Import packages.
import json
import boto3
 
 # Initalize parameters.
config = boto3.client('config')
compliance_value = 'NOT_APPLICABLE'

def handler(event, context):
    
    invoking_event = json.loads(event['invokingEvent'])
    rule_parameters = json.loads(event['ruleParameters'])

    item = invoking_event['configurationItem']

    if is_applicable(item, event):
        compliance_value = evaluate_compliance(item, rule_parameters)

    config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': item['resourceType'],
                'ComplianceResourceId': item['resourceId'],
                'ComplianceType': compliance_value,
                'OrderingTimestamp': item['configurationItemCaptureTime']
            },
        ],
        ResultToken=event['resultToken'])

def is_applicable(item, event):

    status = item['configurationItemStatus']
    event_left_scope = event['eventLeftScope']
    test = ((status in ['OK', 'ResourceDiscovered']) and
            event_left_scope is False)
    return test

def evaluate_compliance(config_item, rule_parameters):
 
    if len(config_item['configuration']['tags']) <= 1:
        return 'NON_COMPLIANT'
    elif len(config_item['configuration']['tags']) > 1:
        return 'COMPLIANT'
    else:    
        return 'NOT_APPLICABLE'