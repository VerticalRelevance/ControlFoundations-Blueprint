# AWS Controls Foundation - Controls Pipeline Repository

This is the Control Foundations Blueprint repo for Vertical Relevance's AWS Control Foundation solution. This
is the repository that will deploy preventative and detective security controls such as AWS Config
with Conformance Packs and custom rules, GuardDuty, IAM Access Analyzer, Macie, and a Control Broker using AWS Config.

## Prior to starting the setup of the CDK environment, ensure that you have cloned this repo.

## Follow the setup steps below to properly configure the environment and first deployment of the infrastructure.

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
# The following can be left blank to have a connection created for you
codestar_connection_arn = <codestar-connection-arn>
```

Bootstrap the cdk app.

```
cdk bootstrap
```

At this point you can deploy the CDK app for this blueprint.

```
$ cdk deploy --all
```

After running cdk deploy, the 2 pipeline structures will be set up.

If you configured the solution to create a CodeStar connection for you, you will
need to go into the console and manually authenticate each pipeline against git
by editing the source artifact stage of the pipeline. Once they are
authenticated, you will not need to perform this manual step again unless you
rebuild the source artifact construct. See [these AWS docs](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-update.html) for instructions on doing this. Once the connection is set up, you may have to start a new run of the pipeline manually by clicking
"Release Change" on the pipeline page(s) of the console, or push some code to
kick off a new pipeline run automatically.

## Development/Contribution

To add additional dependencies, for example other CDK libraries, just add
them to your `requirements.txt` file and rerun the `pip install -r requirements.txt`
command. It is preferable to use `pip freeze -r requirements.txt > requirements.txt`
to generate `requirements.txt` with every required package and the required
version of each rather than adding the package to requirements.txt without a
version specfifier. Just make sure to edit the `-e <github URL>` line to be `-e .`
before committing, since `pip freeze` freezes the exact GitHub commit hash URL for
installation, which could break your setup in the future.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## Screenshots

Once you have deployed the solution, you should see a pipeline like the following:

![Screenshot 2021-09-28 at 11-28-20 CodePipeline - AWS Developer Tools](https://user-images.githubusercontent.com/5383250/135118103-7cf76769-7030-4cc5-8190-a73b9b8b8645.png)

