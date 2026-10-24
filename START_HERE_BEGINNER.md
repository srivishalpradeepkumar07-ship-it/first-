# Start Here: EduTechX Chatbot Beginner Guide to Build and Host an AI Chatbot on AWS

This guide assumes Windows 10/11 and no previous cloud experience. Follow the steps in order. Do not skip the cost and credential-safety steps.

## What you will build

## EduTechX branding and Xylo

The project uses the exact robot image supplied for this project as both the header logo and the animated flying mascot named **Xylo**. The original image is stored in `static/edutechx-logo.png` and `static/edutechx-bot.png`; these two files intentionally contain the same uploaded image.


A browser-based chatbot with:
- **Python + Flask** for the web application
- **Amazon Bedrock** to generate AI answers
- **AWS Elastic Beanstalk** to host the application (on Amazon EC2)

The starter project is a learning demo, not a production-secure public chatbot.

## Before you start

You need:
1. A Windows computer and internet access.
2. An AWS account or an instructor-provided training account.
3. Permission to use Amazon Bedrock and Elastic Beanstalk. A company or classroom AWS administrator may need to grant this.
4. The ZIP file supplied with this guide.

**Cost warning:** AWS resources can incur charges. Set a small AWS Budget and email alert before deploying. A budget alert is not a hard spending limit and does not automatically stop services.

## Phase 1 — Install the tools

### Step 1. Install Python

1. Open the official Windows downloads page: https://www.python.org/downloads/windows/
2. Download a supported 64-bit Python version (Python 3.11 or newer is suitable for local practice).
3. Run the installer. On the first installer screen, tick **Add python.exe to PATH**, then choose **Install Now**.
4. Close any old Command Prompt or PowerShell windows and open a new PowerShell window.
5. Check the installation:

```powershell
py --version
python --version
```

You should see a Python 3 version number. If Windows says the command is not found, reopen PowerShell; if it still fails, reinstall Python and make sure it was added to PATH.

### Step 2. Install Visual Studio Code (recommended)

1. Download VS Code from https://code.visualstudio.com/
2. Install it using the normal installer options.
3. Open VS Code. Choose **File → Open Folder** later to open this project.

### Step 3. Install AWS CLI

The AWS CLI is useful when you are allowed to sign in locally and test Bedrock from your computer. It is not required just to upload the ZIP through the AWS Console.

1. Follow the official Windows installation steps: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. Close and reopen PowerShell.
3. Verify:

```powershell
aws --version
```

You should see a line starting with `aws-cli/2`.

## Phase 2 — Prepare the project on your computer

### Step 4. Extract the project ZIP

1. Download `EdutechX-Cloud-DevOps-Chatbot.zip`.
2. In File Explorer, right-click the ZIP and choose **Extract All**.
3. Open the extracted folder. You should see `application.py`, `requirements.txt`, `Procfile`, and a `templates` folder containing `index.html`.
4. Do not upload or share AWS passwords, tokens, or credential files with the project.

### Step 5. Open a terminal in the project folder

Easy method:
1. Open the extracted project folder in File Explorer.
2. Click the address bar, type `powershell`, and press Enter.
3. PowerShell should open with this folder as its current directory.

Run:

```powershell
Get-ChildItem
```

Confirm that `application.py` and `requirements.txt` are listed.

### Step 6. Create a Python virtual environment

Copy and run these commands one at a time:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

After activation, the prompt usually begins with `(.venv)`. The last command installs Flask, Boto3, and Gunicorn. Wait for it to finish without an error.

If PowerShell blocks the activation script, run this command in the same PowerShell window, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This changes script policy only for the current PowerShell process.

### Step 7. Run the local web app in guided demo mode (optional)

The app uses live Bedrock mode by default. If you want to first test the flying robot UI, welcome message, learning paths, and prepared course conversations without AWS credentials or model charges, explicitly enable guided demo mode:

Start the app:

```powershell
$env:CHATBOT_DEMO_MODE = "true"
python application.py
```

Leave that PowerShell window open. It is running the server.

Open a browser and visit:
- Chat page: http://127.0.0.1:5000
- Health test: http://127.0.0.1:5000/health

The health page should show JSON containing `"status":"ok"`. This confirms that Flask is running.

**Expected result:** the page shows the EduTechX logo, a flying robot named Xylo, “Welcome to EDUTECHX! What’s up today?”, and suggested Cloud, DevOps, and Engineering prompts. Click a topic and the bot will reply with a guided sample. The `/health` endpoint should report `"mode":"demo"`.

**To use real AI responses on your computer**, stop the demo server with `Ctrl+C`, configure an approved AWS identity, and in the same PowerShell window set:

```powershell
$env:CHATBOT_DEMO_MODE = "false"
$env:AWS_REGION = "us-east-1"
$env:BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
python application.py
```

Live AI mode also requires an approved AWS identity, access to the selected Bedrock model, and permission to invoke it. If you do not have approved local AWS access, continue to the AWS deployment steps instead.

To stop the local server, return to PowerShell and press **Ctrl+C**.

## Phase 3 — Prepare AWS safely

### Step 8. Sign in and set a budget alert

1. Sign in to the AWS Console using your training account or personal account.
2. For a personal account, enable multi-factor authentication (MFA) on the root user and avoid using the root user for daily development.
3. Open **Billing and Cost Management → Budgets → Create budget**.
4. Create a small monthly cost budget appropriate for your own currency/budget and add an email alert at a low threshold.
5. Confirm that the alert email is correct.

Budget alerts help you notice spending; they are not guaranteed to stop it. The web environment and AI model calls may both cost money.

Official guide: https://docs.aws.amazon.com/cost-management/latest/userguide/create-cost-budget.html

### Step 9. Choose one AWS Region

For the starter configuration, use **US East (N. Virginia), `us-east-1`**, where `amazon.nova-lite-v1:0` has an in-region endpoint. For another region, first confirm that your selected Bedrock model and Elastic Beanstalk platform are available there.

Keep the application's `AWS_REGION` and the deployed environment's region aligned with your model choice. Official model information: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html

### Step 10. Test the model in the Bedrock Console

1. In the AWS Console's Region selector, choose `us-east-1`.
2. Search for **Amazon Bedrock**.
3. Open the model catalog/playground and find **Amazon Nova Lite**.
4. If prompted, review the model terms and required access setup. Model availability and permissions depend on the account and region.
5. Open the text playground, type a simple prompt such as `Explain Python variables in three bullet points`, and run it.
6. Continue only after you get a response.

If the model is missing or access is denied, ask the AWS administrator to check the account permissions, region, model requirements, and billing setup.

## Phase 4 — Deploy to AWS Elastic Beanstalk

### Step 11. Create a web application environment

1. In the same region (`us-east-1`), open **AWS Elastic Beanstalk**.
2. Choose **Create application**.
3. Give it a simple name, for example `classroom-ai-chatbot`.
4. Choose to create a **Web server environment**.
5. For the managed platform, select a Python platform branch currently offered in the console.
6. For the application code/source, choose **Upload your code** and select the supplied `EdutechX-Cloud-DevOps-Chatbot.zip` file.
7. If the console offers a single-instance environment type, use it for a short classroom demonstration to avoid adding a load balancer unnecessarily.
8. Review settings and create the environment.

The ZIP's application files must be at the ZIP root: `application.py`, `requirements.txt`, `Procfile`, `templates/index.html`, and the `static/` folder that contains the EduTechX logo and robot mascot. Do not upload the `.venv` folder.

### Step 12. Configure the EC2 instance role

The app needs permission to call Bedrock. Do not place access keys in the code or environment variables.

1. During environment creation, look for **Service access**, **EC2 instance profile**, or **Permissions**. The service role and EC2 instance profile serve different purposes; the app's Bedrock permission must be on the **EC2 instance profile role**.
2. If the console asks you to create an instance profile role, use the Elastic Beanstalk compute/EC2 role path and attach the Elastic Beanstalk policies recommended by the console/documentation. A common needed policy is `AWSElasticBeanstalkWebTier`.
3. After the role exists, open **IAM → Roles** and select the EC2 instance profile role used by this environment.
4. Add an inline or customer-managed policy allowing `bedrock:InvokeModel` only for the model the app uses. For the sample model in `us-east-1`, this resource ARN is:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeNovaLiteForClassroomChatbot",
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0"
    }
  ]
}
```

5. Save the policy. Confirm that the role you edited is the one assigned as the environment's EC2 instance profile. If you select a different model or inference profile, change the resource to the matching ARN.

Official role guide: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-instanceprofile.html

### Step 13. Set the application's environment properties

In Elastic Beanstalk, open your environment and choose **Configuration**. Find the section named **Software**, **Environment properties**, or its current equivalent. Add these properties:

| Name | Value |
|---|---|
| `AWS_REGION` | `us-east-1` |
| `BEDROCK_MODEL_ID` | `amazon.nova-lite-v1:0` |
| `CHATBOT_DEMO_MODE` | `false` |

Save/apply the configuration and allow the environment to update.

### Step 14. Test the hosted chatbot

1. Wait until the environment health is **Green/OK**. Confirm that `CHATBOT_DEMO_MODE` is set to `false` if you want live AI replies rather than guided demo replies.
2. Open the environment URL shown in Elastic Beanstalk.
3. Add `/health` to the URL. It should return JSON with `"status":"ok"`.
4. Return to the home page and ask: `Explain Python lists with a short example`.
5. If you get a response, the project is working in AWS.

Do not publish the URL widely yet. The starter app does not include sign-in, rate limiting, or protections appropriate for an unrestricted public AI service.

## Phase 5 — If something goes wrong

- **`py` is not recognized:** reinstall Python and tick **Add python.exe to PATH**, then open a new terminal.
- **`pip install` fails:** confirm the terminal is in the project folder and the virtual environment is active.
- **The web page will not open:** confirm `python application.py` is still running; try `http://127.0.0.1:5000`.
- **`/health` works but AI replies fail:** the web server works; check Bedrock model ID, region, model availability, instance profile, and `bedrock:InvokeModel` permission. Open Elastic Beanstalk logs for the server-side error.
- **`AccessDeniedException`:** the active IAM identity/role likely lacks a needed permission or model setup is incomplete.
- **`Model not found` or validation error:** check the model ID and region in both the Bedrock Console and environment properties.
- **Deployment fails:** review Elastic Beanstalk events and logs; confirm the ZIP contents are at its root.

## Phase 6 — Stop charges after practice

When finished:
1. Open Elastic Beanstalk → your environment → **Actions → Terminate environment** and confirm.
2. Check the EC2 console for any leftover instances, volumes, or elastic IP addresses.
3. Review AWS Billing and Cost Management and Bedrock usage.
4. Keep the project files on your computer; terminating the environment does not delete the local ZIP.

## Suggested student exercises

1. Change the system prompt in `application.py` so the bot behaves as a Python tutor.
2. Ask it five Python questions and record the outputs.
3. Explain the purpose of Flask, Boto3, Bedrock, IAM roles, and Elastic Beanstalk.
4. Add three suggested prompt buttons to the user interface.
5. Explain why the application uses an EC2 instance role instead of hard-coded AWS access keys.

## Official AWS references

- Install AWS CLI on Windows: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Flask on Elastic Beanstalk: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
- Elastic Beanstalk EC2 instance profile: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-instanceprofile.html
- Use Bedrock with Boto3: https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api-ex-python.html
- Nova Lite model ID and region details: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html
- Create a cost budget: https://docs.aws.amazon.com/cost-management/latest/userguide/create-cost-budget.html
