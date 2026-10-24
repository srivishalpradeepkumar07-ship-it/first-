# Student Lab: EduTechX Cloud & DevOps Chatbot

## Learning outcomes

By the end, you should be able to:

- explain the roles of Python, Flask, an HTTP endpoint, `boto3`, IAM and Amazon Bedrock;
- run and test a Flask application locally;
- explain the difference between guided demo replies and AI-generated Bedrock replies;
- call an AI model through the Bedrock Converse API;
- deploy a Python app to AWS Elastic Beanstalk;
- check application health and diagnose common IAM/model errors;
- clean up cloud resources after the lab.

## Lab prerequisites

Python installed and a code editor. The guided demo works before AWS setup. Live AI and cloud deployment additionally require instructor-approved AWS Console access, a selected Bedrock model/Region, and a budget or classroom account. Do not put personal credentials in source code or share them with teammates.

## Part A — Run the starter project

1. Unzip the provided EduTechX project.
2. In the project folder, create and activate a virtual environment.
3. Install packages from `requirements.txt`.
4. Run `$env:CHATBOT_DEMO_MODE = "true"` and then `python application.py`.
5. Open `http://127.0.0.1:5000`; try the welcome flow, Cloud Computing button, and DevOps button.
6. Test `/health`; the mode should be `demo`.
7. For live AI, set `CHATBOT_DEMO_MODE` to `false`, set the approved `AWS_REGION` and `BEDROCK_MODEL_ID`, sign in using the classroom-approved AWS method, and test again.

### Record

- Python version:
- AWS Region:
- Model ID:
- Health-check result:
- One question that worked well:
- One question that needed a better prompt:

## Part B — Understand the code

1. Find the Flask application object named `application`.
2. Identify what the `/` route returns.
3. Identify what the `/chat` endpoint accepts and returns.
4. Find the call to `client.converse()` and describe the roles of `modelId`, `messages`, and `system`.
5. Explain why AWS credentials are not stored in the Python file.

## Part C — Deploy to AWS

Follow the instructor's account and budget rules.

1. Confirm the chosen Bedrock model works in the selected AWS Region.
2. Create an Elastic Beanstalk web server environment using a supported Python platform.
3. Upload the starter ZIP with the source files at the root.
4. Give the environment's EC2 instance role only the permissions needed for the app, including model invocation.
5. Set `AWS_REGION`, `BEDROCK_MODEL_ID`, and `CHATBOT_DEMO_MODE=false` as environment variables.
6. Wait for a healthy environment and test `/health` and the chatbot URL.
7. Check application logs if the chat returns an error.

### Evidence checklist

- [ ] Public or instructor-approved app URL opens
- [ ] `/health` returns JSON with status `ok`
- [ ] AI response appears after a question
- [ ] No AWS keys committed to source code
- [ ] App logs reviewed after a test
- [ ] Environment terminated after the exercise (unless instructor says otherwise)

## Part D — Challenge tasks

Choose any two:

1. Update the system prompt to act as an AAI JE exam tutor or a DevOps tutor.
2. Add a “Explain like I’m a beginner” quick prompt.
3. Add a character counter and disable Send for empty messages.
4. Change the maximum response token setting and compare output length.
5. Add a basic server-side request limit, then explain why an in-memory limit is not sufficient for multiple instances.
6. Write a one-page diagram showing browser → Flask → Bedrock → browser.
7. Make a test table with five questions, correctness/quality notes, latency and the likely cost factors.

## Submission

Submit a screenshot of the working local app, the approved cloud URL or instructor-approved deployment evidence, a short architecture diagram, answers to Part B, and the cleanup confirmation.

## Safety rules

- Never enter or share AWS access keys, passwords, personal data, or confidential company material.
- Never make IAM users/roles administrator just to get past an error.
- Do not leave the environment running after class.
- Follow the instructor's shared-account policy; do not deploy 30 separate copies unless the budget and permissions explicitly allow it.


## EduTechX challenge

1. Find the welcome greeting in `templates/index.html` and personalise it without changing the brand name.
2. Add one new suggested prompt button for a topic such as Linux, Git, Docker, or AWS S3.
3. Test both the Cloud Computing and DevOps paths. Record one concept and one hands-on project from each.
4. Explain the difference between guided demo replies and live Amazon Bedrock AI replies.
5. Do not place AWS access keys or passwords in source code, HTML, or screenshots.
