# Instructor Guide — EduTechX Cloud & DevOps Chatbot Hands-on

## Suggested 3-hour session

| Time | Activity | Deliverable |
|---|---|---|
| 0:00–0:15 | Show the user flow and architecture | Students label the 4 components |
| 0:15–0:35 | Python virtual environment, dependencies and Flask basics | Branded EduTechX chat opens locally in demo mode |
| 0:35–1:00 | Explore Cloud/DevOps demo prompts, then read `/chat`, JSON, `boto3`, and Bedrock Converse API | Students explain guided demo vs live AI |
| 1:00–1:15 | Short break / troubleshooting | Checklist |
| 1:15–1:40 | IAM roles, model ID, Region, credentials chain | Successful local model response |
| 1:40–2:20 | Demonstrate Elastic Beanstalk deploy | Instructor deployment or small groups |
| 2:20–2:45 | Student modifications/challenge tasks | Changed prompt or UI |
| 2:45–3:00 | Cost review, security recap and cleanup | Environment cleanup confirmed |

For a shorter 90-minute session, do the local setup and Bedrock call live, then use a pre-deployed instructor instance for the cloud-demo portion. Do not require every student to create billable cloud resources unless the course account is prepared for it.

## Before class

- Confirm the classroom AWS account and allowed regions.
- Verify the selected model is available and can be invoked in that account.
- Create a least-privilege role/policy for the demo.
- Create a budget and alert; use a single shared instructor deployment where appropriate.
- Test the ZIP upload and the app's health route.
- Prepare a fallback screenshot or local demonstration if model access is not enabled.
- Have students work with synthetic questions only; do not paste secrets or workplace-confidential information.

## Assessment rubric (20 points)

| Criterion | Points |
|---|---:|
| Runs the local Flask app and tests health endpoint | 4 |
| Explains request flow and Converse API | 4 |
| Correct IAM/Region/model configuration | 4 |
| Deploys or documents a successful approved cloud test | 4 |
| Completes one extension and explains cleanup/security | 4 |

## Instructor prompts

- Why should the browser never call Bedrock with an embedded secret?
- What is the difference between local AWS CLI credentials and an EC2 instance role?
- What could cause a 502 response from `/chat`?
- What AWS costs remain if the URL is no longer being used?
- How would the design change for many users, persistent history, login, or uploaded documents?
