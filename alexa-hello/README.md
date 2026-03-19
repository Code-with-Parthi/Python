# Alexa Hello Sample (Echo Show)

This repository contains a minimal Alexa skill that responds with a greeting and renders a simple APL (visual) document on Echo Show devices.

Files added:
- [skill.py](alexa-hello/skill.py) - Lambda handler (Python, Ask SDK)
- [apl/hello_apl.json](alexa-hello/apl/hello_apl.json) - APL document shown on Echo Show
- [interactionModel.json](alexa-hello/interactionModel.json) - Interaction model to import into the Alexa Developer Console
- [requirements.txt](alexa-hello/requirements.txt) - Python dependency list for packaging

Prerequisites
- An AWS account with permissions to create Lambda functions and IAM roles
- An Alexa Developer account (developer.amazon.com)
- `aws` CLI configured (optional, for uploading from CLI)
- Python 3.8+ and `pip`

Quick overview
1. Package the Lambda function and dependencies
2. Create an AWS Lambda function and upload the zip
3. Create an Alexa Skill in the Developer Console and point its endpoint to the Lambda ARN
4. Enable the APL interface for the skill and import the interaction model
5. Test on an Echo Show or the Alexa simulator

Packaging the Lambda (recommended simple method)
1. Create a packaging directory and install dependencies there:

```bash
cd alexa-hello
mkdir package
pip install -r requirements.txt -t package/
```

2. Copy your code and APL into the package directory and zip:

```bash
cp skill.py package/
cp -r apl package/
cd package
zip -r ../function.zip .
cd ..
```

3. Upload the zip in the AWS Lambda console (create function -> Author from scratch -> Python 3.8+, set execution role). Or update via CLI:

```bash
aws lambda create-function --function-name AlexaHelloSample \
  --runtime python3.8 --role <ROLE_ARN> --handler skill.lambda_handler \
  --zip-file fileb://function.zip
# or, if function already exists:
aws lambda update-function-code --function-name AlexaHelloSample --zip-file fileb://function.zip
```

IAM role notes
- The Lambda function needs a basic execution role (AWSLambdaBasicExecutionRole) so it can write logs to CloudWatch. Create via console or use a role ARN when creating the function.

Create the Alexa Skill (Developer Console)
1. Go to developer.amazon.com -> Alexa -> Create Skill
2. Choose a name (e.g., "Hello Sample"), select "Custom" model and choose a template "Start from scratch"
3. Set the invocation name to `hello sample` (matches interactionModel.json)
4. In the left menu, open JSON Editor under Interaction Model, replace the model with the contents of `interactionModel.json`, then build the model
5. In the left menu, open Endpoint -> choose AWS Lambda ARN and paste the ARN from the Lambda you created
6. In Build -> Interfaces, enable "Alexa Presentation Language (APL)" so Echo Show devices will render visual output

Testing
- Use the Test tab in the Developer Console (enable testing) and type or speak "open hello sample" or "ask hello sample to say hello".
- On a physical Echo Show linked to the same Amazon account, say "Alexa, open hello sample".
 - Ask for the current time: "ask hello sample what time is it" or "ask hello sample to tell me the time".
 - On a physical Echo Show linked to the same Amazon account, say "Alexa, open hello sample".
 - News example:
   - Read Vikatan headlines: "ask hello sample to read vikatan news" or "ask hello sample what's the news".

Notes and tips
- When packaging locally, ensure `ask-sdk-core` is included in the zip (installed into `package/` as shown).
- For iterative development, you can use the AWS SAM or Serverless frameworks for smoother deployment.
- If the APL document does not render, verify the device supports APL and that APL is enabled in the skill's Interfaces.

Further improvements
- Add more intents and slot types
- Use datasources in the APL document for dynamic content
- Use AWS SAM for CI-friendly deployments
