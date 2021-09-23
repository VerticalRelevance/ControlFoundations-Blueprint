# Control Broker OPA Lambda

This function code is taken and modified from [the AWS-Config-OPA AWS Management and Governance samples](https://github.com/aws-samples/aws-management-and-governance-samples/tree/4be655006d9a84724001c7dd3bcf81a47d871bd8/AWSConfig/AWS-Config-OPA).
Its general usage is described in [Using OPA to create AWS Config rules](https://aws.amazon.com/blogs/mt/using-opa-to-create-aws-config-rules/)
from the AWS Blog.

This lambda function is meant to listen to AWS config events and return a
compliance status.

When it receives an actionable event, it executes the OPA binary with the
corresponding OPA rego file and the incoming event data. The code depends on the
config event's `ruleParameters` (specified as `InputParameters` in a CFN
template), specifically `ASSETS_BUCKET`, `REGO_POLICIES_PREFIX`, and `REGO_POLICY_KEY` to know which OPA Rego file to obtain from where. This is configured via a Config Rule that points to the Control Broker Lambda Function. The specific OPA package and rule it checks for compliance are specified with the `OPA_POLICY_PACKAGE_NAME` and `OPA_POLICY_RULE_TO_EVAL` input parameters.

For instance, given the following settings:

```
  OpaConfigRule:
    Type: AWS::Config::ConfigRule
    Properties:
      InputParameters:
        ASSETS_BUCKET: assetsbucket
        REGO_POLICIES_PREFIX: opa_policies
        REGO_POLICY_KEY: s3_encryption.rego
        OPA_POLICY_PACKAGE_NAME: policies.s3_encryption
        OPA_POLICY_RULE_TO_EVAL: compliant
      Scope:
        ComplianceResourceTypes: !Ref ConfigRuleScope
      Source:
        Owner: CUSTOM_LAMBDA
        SourceDetails:
          - EventSource: aws.config
            MessageType: ConfigurationItemChangeNotification
        SourceIdentifier: !ImportValue opa-lambda-arn
```

The Lambda would react to config events scoped by `ConfigRuleScope` and pull the `opa_policies/s3_encryption.rego` file from the `assetsbucket` bucket.

If the `s3_encryption.rego` file looked like the following:

```
package policies.s3_encryption

default compliant = false

compliant = true {
    input.resourceType == "AWS::S3::Bucket"

    any([
        input.supplementaryConfiguration.ServerSideEncryptionConfiguration.rules[_].applyServerSideEncryptionByDefault.sseAlgorithm == "AES256",
        input.supplementaryConfiguration.ServerSideEncryptionConfiguration.rules[_].applyServerSideEncryptionByDefault.sseAlgorithm == "aws:kms"
    ])
}
```

The Lambda Function would evaluate this policy using the `opa` binary and, if the value of `compliant` were `true`, it would return the status `COMPLIANT`. Otherwise, it would return `NON_COMPLIANT`.