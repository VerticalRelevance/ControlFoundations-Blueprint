import boto3

region = 'us-east-2'
ec2 = boto3.client('ec2', region_name=region)
config_client = boto3.client('config')
my_rule = "DetectEc2TagViolation"

def handler(event, context):
    non_compliance_detail = config_client.get_compliance_details_by_config_rule(
        ConfigRuleName = my_rule, ComplianceTypes = ['NON_COMPLIANT'])

    if len(non_compliance_detail['EvaluationResults']) > 0:

        non_compliant_resources = ''

        for result in non_compliance_detail['EvaluationResults']:
            print(result['EvaluationResultIdentifier']['EvaluationResultQualifier']
                    ['ResourceId'])
            non_compliant_resources = non_compliant_resources + result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'] + '\n'
        
        resource_type = result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceType']

        if resource_type == 'AWS::EC2::Instance' and non_compliance_detail:
            ec2.stop_instances(InstanceIds= result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'])