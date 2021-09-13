# AWS Controls Foundation - Controls Pipeline Repository

<<<<<<< HEAD
# AWS Controls Foundation - Controls Pipeline Repository

This is the Conrols Pipeline Respository for the AWS Controls Foundation. This is the repository that will host the security controls such as AWS Config Conformance Packs, GuardDuty, IAM Access Analyzer, and Macie.

=======
This is the Conrols Pipeline Respository for the AWS Controls Foundation. This is the repository that will host the security controls such as AWS Config Conformance Packs, GuardDuty, IAM Access Analyzer, and Macie.

>>>>>>> 3a13cc7c06a555ceaa62d780e71bf6c800ecbda2
Follow the setup steps below to properly configure the environment and first deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```
Now that the environment is configured, the last step before deploying is you need to enter your desired git owner and git repos in the parameters section of the app.py file.
```
# Input parameters. Update according to your github owner and repo.
github_owner = <github-account>
controls_repo = <controls-pipeline-repo-name>
application_repo = <application-pipeline-repo-name>
```

At this point you can now deploy the CloudFormation template for this code.
<<<<<<< HEAD

```
$ cdk deploy
```
=======
>>>>>>> 3a13cc7c06a555ceaa62d780e71bf6c800ecbda2

Now that you have deployed the two pipelines, you need to manually authenticate the pipelines against their respective git repos.
```
<<<<<<< HEAD
=======
$ cdk deploy
```

Now that you have deployed the two pipelines, you need to manually authenticate the pipelines against their respective git repos.
```
>>>>>>> 3a13cc7c06a555ceaa62d780e71bf6c800ecbda2
After running cdk deploy, the 2 pipeline structures will be set up, but you will ned to go into the console and manually authenticate each pipeline against git by editing the source artifact stage of the pipeline. Once they are authenticated, you will not need to perform this manual step again unless you rebuild the source artifact construct.
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
