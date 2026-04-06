# Alexa Kid's Classes Manager

This is a complete Alexa skill for managing kids' extracurricular and sports classes, including scheduling, attendance tracking, payment reminders, and completion tracking.

## Features

- **Add Classes**: Add new classes with day, time, instructor, and cost
- **List Classes**: View all scheduled classes
- **Record Attendance**: Mark attendance for each class
- **Attendance Reports**: Check attendance rate per class
- **Payment Tracking**: Track and update payment status for classes
- **Payment Reminders**: Check payment status anytime

## Files

- `skill.py` — Lambda handler with all intents (Add/List/Attendance/Payments)
- `interactionModel.json` — Interaction model for Alexa Developer Console
- `requirements.txt` — Python dependencies
- `package.sh` — Packaging script for Lambda
- `README.md` — This file

## Prerequisites

- An AWS account with Lambda permissions (or use Alexa-hosted)
- An Alexa Developer account (developer.amazon.com)
- Python 3.8+ and pip (for local packaging)
- AWS CLI configured (optional, for CLI deployment)

## Quick Setup

### 1. Package the Skill

```bash
cd alexa-kid-classes
chmod +x package.sh
./package.sh
ls -lh function.zip
```

This creates `function.zip` (~4.4MB) with dependencies.

### 2. Deploy to AWS Lambda

**Option A: AWS Console**
1. Go to AWS Lambda Console
2. Create Function → Author from Scratch
3. Runtime: Python 3.8+
4. Execution Role: Create new with AWSLambdaBasicExecutionRole
5. Upload `function.zip` as zip file
6. Handler: `skill.lambda_handler`
7. Copy the Function ARN

**Option B: AWS CLI**
```bash
# Create function (first time)
aws lambda create-function --function-name AlexaKidClasses \
  --runtime python3.8 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler skill.lambda_handler \
  --zip-file fileb://function.zip

# Update function (subsequent times)
aws lambda update-function-code --function-name AlexaKidClasses \
  --zip-file fileb://function.zip
```

**Option C: Alexa-Hosted (No AWS Account Needed)**
1. Go to Alexa Developer Console → Create Skill
2. Choose name, model: Custom, backend: Alexa-hosted (Python)
3. In Code editor, paste `skill.py` code
4. Update `interactionModel.json` via JSON Editor
5. Build & Deploy

### 3. Create Alexa Skill in Developer Console

1. Go to developer.amazon.com/alexa
2. Create Skill
   - Name: Kid's Classes Manager
   - Model: Custom
   - Hosting: AWS Lambda (or Alexa-hosted)
3. Interaction Model:
   - Open JSON Editor
   - Paste contents of `interactionModel.json`
   - Click Build Model
4. Endpoint:
   - Choose AWS Lambda ARN
   - Paste your Lambda ARN
5. Interfaces:
   - Enable Alexa Presentation Language (APL) if using Echo Show (optional)

### 4. Test the Skill

In Developer Console Test tab (enable testing):
```
User: "open kid classes"
Response: Welcome message

User: "add piano on Monday at 4 PM taught by John Smith for 50 dollars"
Response: Added piano to the schedule.

User: "list my classes"
Response: Piano on Monday at 4 PM, taught by John Smith.

User: "record attendance for piano"
Response: Did the child attend or miss?

User: "attended"
Response: Recorded attended for piano on [today's date].

User: "attendance for piano"
Response: Piano: 1 out of 1 classes attended, that's 100% attendance rate.

User: "check payment for piano"
Response: Payment for piano is pending. Cost is 50 dollars.

User: "update payment for piano to paid"
Response: Updated piano payment status to paid.
```

## Intent Reference

### AddClassIntent
Adds a new class to the schedule.

Sample utterances:
- "add piano"
- "add piano on Monday at 4 PM"
- "add piano taught by John Smith"
- "add piano on Monday at 4 PM with John Smith for 50 dollars"

Slots:
- `ClassName` (required): Name of the class
- `Day` (optional): Day of week
- `Time` (optional): Time of class
- `Instructor` (optional): Instructor name
- `Cost` (optional): Cost in dollars

### ListClassesIntent
Lists all scheduled classes.

Sample utterances:
- "list my classes"
- "show all classes"
- "what classes are scheduled"

### RecordAttendanceIntent
Records attendance for a specific class.

Sample utterances:
- "record attendance for piano"
- "mark piano as attended"

Slots:
- `ClassName` (required): Class name
- `AttendanceStatus` (required): attended, missed, etc.

### CheckPaymentIntent
Checks payment status for a class or all classes.

Sample utterances:
- "check payment for piano"
- "what's the payment status"
- "is piano paid"

Slots:
- `ClassName` (optional): Class name (if omitted, returns all)

### UpdatePaymentIntent
Updates payment status for a class.

Sample utterances:
- "mark piano as paid"
- "update payment for piano to paid"

Slots:
- `ClassName` (required): Class name
- `PaymentStatus` (required): paid, pending, etc.

### AttendanceReportIntent
Shows attendance rate for a specific class.

Sample utterances:
- "attendance for piano"
- "how many classes did the child attend"

Slots:
- `ClassName` (required): Class name

## Data Storage

Classes are stored in JSON format (ephemeral storage in `/tmp/kid_classes.json`):

```json
{
  "piano": {
    "name": "Piano",
    "day": "Monday",
    "time": "4 PM",
    "instructor": "John Smith",
    "cost": "50",
    "attendance": [
      { "date": "2026-04-06", "status": "attended" },
      { "date": "2026-04-13", "status": "attended" }
    ],
    "payment_status": "paid"
  }
}
```

**Note**: Ephemeral storage clears on Lambda cold start. For production, integrate with:
- **DynamoDB**: Persistent storage across invocations
- **S3**: Backup and archival
- **RDS**: Relational database option

## Production Improvements

1. **Persistent Storage**: Replace `/tmp` with DynamoDB or RDS
2. **Authentication**: Add Alexa Skills Kit Sign-in for account linking
3. **Notifications**: Use Alexa Reminders API for payment & attendance alerts
4. **Multi-Child Support**: Add child profiles and distinguish classes per child
5. **Photos/Documents**: Store receipts and class materials in S3
6. **Reporting**: Generate monthly/yearly attendance and expense reports
7. **Alexa Shopping List**: Auto-add supplies/uniforms to shopping list
8. **Alexa Routines**: Trigger reminders via custom Routines

## Troubleshooting

**Skill not triggering intents:**
- Verify invocation name is "kid classes"
- Check interaction model was built successfully
- Ensure Lambda ARN is correct in endpoint
- Review CloudWatch logs for errors

**Attendance/payment not saving:**
- Ephemeral storage clears on cold start; use DynamoDB for persistence
- Check IAM role has CloudWatch Logs permissions

**Slow responses:**
- Lambda cold start is normal (1-2s)
- Optimize by reducing zip size or using provisioned concurrency

## Support & Further Reading

- [Alexa Skills Kit Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
- [Ask SDK for Python](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Alexa Reminders API](https://developer.amazon.com/en-US/docs/alexa/smapi/reminders-api-overview.html)
