import os
from pathlib import Path

from aws_cdk import (
    aws_config,
    aws_s3_assets,
    core as cdk,
    aws_lambda,
    aws_lambda_python,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "controls_scripts")
CONTROL_BROKER_OPA_LAMBDA_LAYER_DIR = os.path.join(
    SCRIPTS_DIR, "lambdas/control_broker_opa_layer"
)
CONTROL_BROKER_LAMBDA_ENTRY_DIR = os.path.join(
    SCRIPTS_DIR, "lambdas/control_broker_opa_lambda"
)
CONTROL_BROKER_LAMBDA_INDEX_FILENAME = "control-broker-opa-lambda.py"
CONTROL_BROKER_LAMBDA_HANDLE_NAME = "lambda_handler"


class ControlBroker(cdk.Construct):
    REGO_POLICIES_PREFIX = "rego_policies"

    def __init__(self, scope: cdk.Construct, id: str) -> None:
        super().__init__(scope, id)
        self.opa_lambda = aws_lambda_python.PythonFunction(
            self,
            "ControlBrokerLambdaFunction",
            entry=CONTROL_BROKER_LAMBDA_ENTRY_DIR,
            index=CONTROL_BROKER_LAMBDA_INDEX_FILENAME,
            handler=CONTROL_BROKER_LAMBDA_HANDLE_NAME,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
        )
        self.opa_layer = aws_lambda.LayerVersion(
            self,
            "OpaLambdaLayer",
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
            layer_version_name="opa-layer",
            description="OPA binary for custom config rules lambda (from the Control Foundations Blueprint)",
            code=aws_lambda.Code.from_asset(CONTROL_BROKER_OPA_LAMBDA_LAYER_DIR),
        )
        self.opa_lambda.add_layers(self.opa_layer)

    def add_opa_rule(
        self,
        local_rego_policy_file_path: Path,
        name: str,
        description: str,
        rule_scope: aws_config.RuleScope,
        opa_policy_package_name: str,
        opa_policy_rule_to_eval: str,
    ):
        rego_policy_asset = aws_s3_assets.Asset(
            self, f"{name}RegoAsset", path=str(local_rego_policy_file_path.resolve())
        )
        rego_policy_asset.grant_read(self.opa_lambda)
        aws_config.CustomRule(
            self,
            name,
            description=description,
            config_rule_name=name,
            lambda_function=self.opa_lambda,
            configuration_changes=True,
            periodic=True,
            rule_scope=rule_scope,
            input_parameters={
                "ASSETS_BUCKET": rego_policy_asset.s3_bucket_name,
                "REGO_POLICIES_PREFIX": "",
                "REGO_POLICY_KEY": rego_policy_asset.s3_object_key,
                "OPA_POLICY_PACKAGE_NAME": opa_policy_package_name,
                "OPA_POLICY_RULE_TO_EVAL": opa_policy_rule_to_eval,
            },
        )
