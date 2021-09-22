# AWS Controls Foundation - Controls Pipeline Repository

This is the Conrols Pipeline Respository for the AWS Controls Foundation. This
is the repository that will host the security controls such as AWS Config
Conformance Packs, GuardDuty, IAM Access Analyzer, and Macie.

## Prior to starting the setup of the CDK environment, ensure that you have done the following things:
* Cloned this repo and the other, ControlsFoundation-ApplicationPipeline

Follow the setup steps below to properly configure the environment and first
deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are on a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Now that the environment is configured, the last step before deploying is you
need to enter your desired git owner and git repos in the parameters section of
the app.py file.

```
# Input parameters. Update according to your github owner and repo.
github_owner = <github-account>
controls_repo = <controls-pipeline-repo-name>
application_repo = <application-pipeline-repo-name>
```

At this point you can deploy the CDK app for this blueprint.

```
$ cdk deploy --app ControlsFoundationControlsPipeline
```

After running cdk deploy, the 2 pipeline structures will be set up, but you will
ned to go into the console and manually authenticate each pipeline against git
by editing the source artifact stage of the pipeline. Once they are
authenticated, you will not need to perform this manual step again unless you
rebuild the source artifact construct.

To add additional dependencies, for example other CDK libraries, just add
them to your `requirements.txt` file and rerun the `pip install -r requirements.txt`
command. It is preferable to use `pip freeze -r requirements.txt > requirements.txt`
to generate `requirements.txt` with every required package and the required
version of each rather than adding the package to requirements.txt without a
version specfifier.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
