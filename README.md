# EduTechX Cloud & DevOps AI Chatbot

> **Beginner? Start with [START_HERE_BEGINNER.md](START_HERE_BEGINNER.md).** It walks through installation, local testing, AWS preparation, deployment, troubleshooting, and cleanup in order.

A beginner-friendly, branded chatbot for **EduTechX**. It features a floating robot mascot, the greeting “Welcome to EDUTECHX! What's up today?”, learning guidance about Cloud Computing, DevOps, and Engineering, and Amazon Bedrock live AI enabled by default. It deploys to **AWS Elastic Beanstalk** (which runs the web app on EC2).

**Brand asset:** the exact robot PNG supplied by the user is used unchanged for both `static/edutechx-logo.png` (header logo) and `static/edutechx-bot.png` (Xylo, the flying robot mascot). The image gently floats in the hero area; the wordmark and tagline are rendered as text beside the logo.

> This is a classroom/demo starter, not a production-ready service. Before public use, add authentication, request throttling, monitoring, and a stricter IAM policy.

## Architecture

Browser chat UI → Flask `/chat` endpoint → guided local course replies (demo mode) OR Amazon Bedrock Converse API with Cloud, DevOps, and Engineering learning guidance (live AI mode) → response → browser.

In either mode, common conversation commands such as greetings, “help,” “thanks,” and “bye” receive immediate local replies. In live mode, other questions are sent to Amazon Bedrock.

Elastic Beanstalk hosts the Flask app on EC2. On AWS, the app should obtain permissions from an EC2 instance role; it should not contain AWS access keys.

## Prerequisites

- Python 3.11+ recommended for local practice (select a currently supported Python platform in Elastic Beanstalk).
- For live AI or cloud hosting: an approved AWS account, budget alert, Bedrock model access, and suitable IAM permissions.
- AWS CLI configured locally for live Bedrock tests, or a suitable IAM role in the deployed AWS environment.
- To use guided demo mode instead, set `CHATBOT_DEMO_MODE` to `true`; demo mode does not call Bedrock.

## Run locally on Windows PowerShell

The project starts in **live AI mode by default**. Configure an approved AWS identity, select a model available to your account, and set the Region before starting the app. Common commands such as greetings, “help,” “thanks,” and “bye” are answered locally in either mode. To practise without AWS, explicitly switch to guided demo mode by setting `CHATBOT_DEMO_MODE` to `true`.

Open PowerShell in this folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For live AI, configure your AWS identity and these settings in the same PowerShell window:

```powershell
$env:CHATBOT_DEMO_MODE = "false"
$env:AWS_REGION = "us-east-1"
$env:BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
aws sts get-caller-identity
python application.py
```

Open `http://127.0.0.1:5000` and check `http://127.0.0.1:5000/health`. The JSON should include `"mode":"bedrock"`. If you have not configured AWS yet, run the guided demo instead:

```powershell
$env:CHATBOT_DEMO_MODE = "true"
python application.py
```

### Switch to live AI answers later

If you started in guided demo mode, stop the server with `Ctrl+C`. Make sure you have an approved AWS sign-in and that the selected model is available, then set these variables in the same PowerShell window:

```powershell
$env:CHATBOT_DEMO_MODE = "false"
$env:AWS_REGION = "us-east-1"
$env:BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
aws sts get-caller-identity
python application.py
```

Use your instructor-approved temporary credentials or IAM Identity Center profile where available. Never use root-account credentials or paste keys into Python files. Live AI mode requires the active AWS identity to have permission to invoke the model.

If PowerShell blocks script activation, use this for the current terminal only or run the activation command in Command Prompt instead:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Configure Amazon Bedrock

1. In the AWS Console, choose the same Region you will use for the app.
2. Open Amazon Bedrock and check that your chosen model is available and usable in that Region/account.
3. Keep `BEDROCK_MODEL_ID` and `AWS_REGION` aligned to your selection. Example values are shown above; model availability and account permissions can vary.
4. For local tests, ensure the identity returned by `aws sts get-caller-identity` has permission to invoke the selected model.

The code uses the Bedrock Converse API through `boto3`. The server does not accept credentials from browser requests.

## Deploy with the AWS Console (no EB CLI required)

### 1. Prepare the source bundle

Create a ZIP containing the **contents** of this project folder at the ZIP root, especially:

- `application.py`
- `requirements.txt`
- `Procfile`
- `templates/index.html`
- `static/edutechx-logo.png` and `static/edutechx-bot.png`

Do not include `.venv`, `__pycache__`, or local credentials. The supplied project ZIP has the application files at the archive root and can be uploaded directly.

### 2. Create an Elastic Beanstalk environment

1. Open **AWS Elastic Beanstalk** in the AWS Console and select your Region.
2. Choose **Create application** and create a **Web server environment**.
3. Pick a currently supported **Python** platform branch. Platform names change over time; use one listed in the console.
4. For a beginner demo, use a **single-instance** environment if the console offers it, rather than a load-balanced setup.
5. Configure the environment and upload the project ZIP as the application code.
6. Create the environment and wait until the health status is green. Open the environment URL.

### 3. Give the EC2 app the right permission

The Elastic Beanstalk environment uses an EC2 instance profile (IAM role). Ensure its role has the standard permissions required for the Beanstalk environment, then add a narrowly scoped policy that allows `bedrock:InvokeModel` for the model you selected. Avoid attaching broad administrator or full Bedrock permissions for a student app. The exact resource ARN should match the model or inference profile and region used in your account; consult the IAM/Bedrock docs when scoping it.

### 4. Set app environment variables

In your Elastic Beanstalk environment's configuration, add these properties to use real AI responses:

- `AWS_REGION` = your chosen AWS Region (for example, `us-east-1`)
- `BEDROCK_MODEL_ID` = your chosen supported model ID (for example, `amazon.nova-lite-v1:0`)
- `CHATBOT_DEMO_MODE` = `false`

Save/apply the configuration and check the environment's health and logs. Visit `/health`, then try a chat message.

## Troubleshooting

- **AccessDenied / not authorized:** check the environment's EC2 instance profile and the `bedrock:InvokeModel` permission.
- **Model not found / validation error:** verify model ID, Region, access and any inference-profile requirements.
- **Local call fails but deployment works (or vice versa):** local credentials and the EC2 instance role are different identities; check each one separately.
- **Application fails to start:** confirm `application.py`, `requirements.txt`, `Procfile`, and `templates/index.html` are at the ZIP root; inspect Elastic Beanstalk logs.
- **HTTP 502 from `/chat`:** inspect application logs for the server-side Bedrock error.

## Cost and cleanup

Elastic Beanstalk itself has no additional service fee, but its underlying AWS resources (notably EC2, storage, and possibly networking/load balancing) are billed. Amazon Bedrock model inference is billed separately. Actual costs depend on region, instance type, request volume, and model. Use AWS Budgets/alerts and a low-usage test. When the class is over, **terminate the Elastic Beanstalk environment** and verify related resources are removed. Also review any Bedrock usage, log storage, IP addresses, volumes, or other resources left behind.

## Student extension ideas

1. Change the system prompt and guided demo replies to make the assistant a Python tutor or another learning helper.
2. Add three quick-prompt buttons in the UI.
3. Add a response-length selector.
4. Add a basic login or classroom access code (do not treat a hard-coded password as production authentication).
5. Add request limits and a persistent conversation store only after discussing privacy and data retention.
6. Compare answers from two available Bedrock models and record response quality, latency and cost.
