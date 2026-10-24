"""EduTechX course-guidance chatbot: Flask + optional Amazon Bedrock AI."""

import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, jsonify, render_template, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

application = Flask(__name__)
application.config["MAX_CONTENT_LENGTH"] = 64 * 1024

DEFAULT_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
DEMO_MODE = os.getenv("CHATBOT_DEMO_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}

SYSTEM_PROMPT = """You are Friday, the warm, encouraging learning guide for EduTechX, whose tagline is
'Empowering Tomorrow's Leaders'. Greet learners naturally and help them explore Cloud Computing
DevOps, and Engineering courses. The learners may be complete beginners, so explain jargon in plain
English, use short headings and practical examples, and suggest manageable hands-on activities.

Cloud Computing learning path: cloud concepts and service models; AWS regions and availability
zones; IAM and security basics; EC2 virtual machines; S3 storage and static website hosting;
VPC networking; managed databases; monitoring and cost awareness; and a small deployment project.

DevOps learning path: SDLC and collaboration; Linux and Bash fundamentals; Git and GitHub; Python
scripting basics; CI/CD pipelines; Docker and containers; Kubernetes fundamentals; Terraform and
Ansible; monitoring; and a practical build-test-deploy project.

Engineering learning path: mathematics and physics fundamentals; engineering design and problem
solving; introductory programming and technical communication; then exploration of disciplines such
as computer, electrical, mechanical, civil, chemical, and biomedical engineering through safe,
beginner-friendly projects. Explain that course and licensing requirements vary by institution and
region. When asked about Engineering, explain what the field does, compare disciplines when useful,
suggest core beginner subjects, and offer safe, low-cost project ideas. For example, discuss paper
bridge designs for civil engineering, simple mechanisms for mechanical engineering, low-voltage
educational circuits for electrical engineering, logic or supervised microcontroller projects for
computer engineering, and process diagrams rather than hazardous experiments for chemical engineering.
Never present a classroom activity as professional engineering advice or a certified design. For
structural, electrical, chemical, medical, or other safety-critical real-world work, recommend a
qualified professional and appropriate supervision.

Explain how Cloud, DevOps, and Engineering complement one another. Do not invent EduTechX fees,
official course durations, certificates, schedules, or guarantees. If asked about those, say the
learner should confirm with the EduTechX team. Ask one helpful follow-up at a time when needed.
Never request passwords, access keys, payment details, or sensitive personal information."""

DEMO_FAQ = (
    (("region", "availability zone", "availability zones"),
     "An AWS **Region** is a separate geographic area where AWS has infrastructure. Each Region contains multiple **Availability Zones**—separate locations designed to reduce the impact of a single location failure. Choose a Region near your users when practical, and check that the services you need are available there."),
    (("iam", "identity and access management"),
     "**AWS IAM** manages identities and permissions. It helps decide who or what can access AWS resources. Start with least privilege: grant only the specific actions and resources needed, and never share passwords or access keys."),
    (("ec2",),
     "**Amazon EC2** provides virtual servers in AWS. You choose a machine size and operating system, then run applications on it. For practice, use a small instance, restrict network access, and stop or delete it when you are finished to avoid ongoing charges."),
    (("s3", "simple storage service"),
     "**Amazon S3** stores files as objects inside buckets. It is commonly used for backups, assets, and static website files. Keep buckets private unless public access is truly required, and avoid uploading sensitive data for practice."),
    (("vpc", "virtual private cloud"),
     "An **Amazon VPC** is a logically isolated network for AWS resources. You define IP ranges and configure subnets, routes, and security controls. A public subnet can have a route to the internet; private subnets are typically used for resources that should not be directly reachable."),
    (("iaas", "paas", "saas", "service model"),
     "**IaaS, PaaS, and SaaS** describe different levels of cloud management. With IaaS, you manage more of the software stack (such as a virtual server). PaaS provides a managed platform for deploying apps. SaaS is ready-to-use software delivered online."),
    (("git", "github", "version control"),
     "**Git** tracks changes to files so you can review work and collaborate. A beginner workflow is: make a branch, edit files, commit a focused change, then push it to a remote such as GitHub. Git is the version-control tool; GitHub is a hosting and collaboration service."),
    (("ci/cd", "continuous integration", "continuous delivery", "pipeline"),
     "**CI/CD** automates steps for building, testing, and delivering software. Continuous integration checks changes frequently; continuous delivery keeps changes ready to release. Start with a pipeline that runs your tests on each code change before adding deployment."),
    (("docker", "container", "containers"),
     "**Docker** packages an application and its dependencies into a container image, helping it run consistently in different environments. Containers share the host operating-system kernel, so they are lighter than full virtual machines. Begin by containerizing a small app and avoid putting secrets in the image."),
    (("kubernetes", "k8s"),
     "**Kubernetes** orchestrates containers across a cluster. It can manage deployment, scaling, and recovery, but it adds concepts and operational complexity. Learn basic containers and networking first; for an early project, Docker alone may be enough."),
    (("terraform", "infrastructure as code"),
     "**Terraform** lets you describe infrastructure in configuration files and create or update it consistently. Review the plan before applying changes, protect state files because they may contain sensitive values, and remove practice resources when finished."),
    (("ansible",),
     "**Ansible** automates configuration tasks on systems, often using readable YAML playbooks. It can install packages and configure services repeatedly. Test a playbook on a disposable machine first and avoid storing passwords or keys in plain text."),
    (("linux", "bash", "shell"),
     "Linux is a common operating system for servers, and **Bash** is a command-line shell used to run commands and scripts. Start with navigation (`pwd`, `ls`, `cd`), file operations, and permissions. Check commands before running them, especially with administrator privileges."),
    (("python", "scripting"),
     "**Python** is a beginner-friendly programming language often used for scripts, web apps, and automation. Practise variables, conditions, loops, functions, and reading error messages, then write a small script that automates a repetitive task."),
)

ENGINEERING_FAQ = (
    (("mechanical engineering",),
     "**Mechanical engineering** applies physics and materials science to machines, motion, energy, and manufactured products. Beginners can explore measurement, simple mechanisms, CAD concepts, and safe design challenges."),
    (("civil engineering",),
     "**Civil engineering** focuses on infrastructure such as buildings, roads, bridges, and water systems. It combines design, materials, structures, and environmental considerations. A beginner project could compare bridge shapes using paper or other safe materials."),
    (("electrical engineering", "electronics engineering"),
     "**Electrical and electronics engineering** study electricity, circuits, signals, and electronic systems. Start with basic voltage, current, and circuit concepts; use low-voltage educational kits and follow safety guidance."),
    (("computer engineering",),
     "**Computer engineering** combines computing with electronics and hardware, including processors, embedded systems, and digital logic. A good first step is learning basic programming and logic circuits, then trying a beginner microcontroller project."),
    (("chemical engineering",),
     "**Chemical engineering** applies chemistry, mathematics, and physics to design processes that make materials and products safely and efficiently. Start with core science and process diagrams; do not try hazardous experiments outside a supervised lab."),
    (("biomedical engineering",),
     "**Biomedical engineering** applies engineering to healthcare, medical devices, and biological systems. It draws on areas such as electronics, mechanics, and biology. Student projects should use safe, non-clinical data and never be treated as medical devices."),
    (("engineering subjects", "engineering study", "study engineering", "engineering degree"),
     "Engineering programs commonly build on **mathematics, physics, design, problem-solving, communication, and teamwork**. The exact subjects and qualifications vary by discipline, institution, and country. Which engineering field are you curious about?"),
    (("engineering project", "engineering projects", "engineering hands-on"),
     "Try a safe beginner engineering project: identify a small everyday problem, sketch a solution, list constraints (cost, size, materials, safety), build a simple prototype from classroom materials, then test and improve it. Keep experiments low-risk and ask an instructor before using tools or electricity."),
)


def get_bedrock_client():
    """Use the standard AWS credentials chain (IAM role in AWS, profile locally)."""
    return boto3.client("bedrock-runtime", region_name=DEFAULT_REGION)

def static_conversation_reply(text):
    """Answer common chat commands locally, including when Bedrock live mode is enabled."""
    q = " ".join(text.lower().strip().split()).strip("!?. ,")
    first_word = q.split(maxsplit=1)[0] if q else ""

    if first_word in {"hello", "hi", "hey", "hello,", "good"} or q.startswith(
        ("good morning", "good afternoon", "good evening", "what's up", "whats up", "start")
    ):
        return (
            "Hey there! 🚀 I'm Friday, your learning buddy. I can help you explore:\n"
            "☁️ Cloud Computing and AWS\n"
            "⚙️ DevOps, Git, Docker, and CI/CD\n"
            "🛠️ Engineering fields and beginner projects\n\n"
            "What would you like to learn about?"
        )
    if q in {"how are you", "how are you doing", "how's it going", "hows it going"}:
        return "I'm doing well and ready to help you learn! 😊 What topic should we explore?"
    if q in {"thanks", "thank you", "thanks xylo", "thank you xylo", "thx"}:
        return "You're welcome! 😊 Ask me anything about Cloud Computing, DevOps, or Engineering whenever you're ready."
    if q in {"bye", "goodbye", "see you", "see you later", "good night"}:
        return "Goodbye for now! 👋 Keep learning, and come back whenever you have another question."
    if q in {"help", "commands", "what can you do", "what can you help with"}:
        return (
            "I can help with Cloud Computing and AWS, DevOps tools and workflows, Engineering fields, "
            "beginner roadmaps, and safe project ideas. Try asking “What is Docker?”, "
            "“Explain computer engineering,” or “Suggest a beginner cloud project.”"
        )
    return None


def demo_reply(text):
    """Beginner-safe local replies so the UI can be practised before AWS is configured."""
    q = text.lower().strip()
    if any(term in q for term in ("fee", "fees", "price", "cost of course", "duration", "certificate", "schedule", "timing")):
        return (
            "I can explain the technical learning path, but I don't have verified EduTechX course fees, official duration, "
            "certificate details, or class schedules. Please confirm those with the EduTechX team so you get accurate information.\n\n"
            "Meanwhile, would you like to see what you can learn in Cloud Computing or DevOps?"
        )
    first_word = q.split(maxsplit=1)[0] if q else ""
    if first_word in {"hello", "hi", "hey", "welcome"} or q.startswith(("what's up", "whats up")) or q == "start":
        return (
            "Hey there! 🚀 I'm Friday, your learning buddy. I'm ready to help you explore the world of cloud and automation.\n\n"
            "Pick a path to get started:\n☁️ Cloud Computing — learn how to use AWS and deploy applications.\n"
            "⚙️ DevOps — learn Git, Docker, CI/CD, and automation.\n"
            "🛠️ Engineering — explore engineering fields, fundamentals, and safe projects.\n\nWhich adventure sounds good today?"
        )
    is_question = "?" in q or q.startswith(
            ("what ", "how ", "why ", "when ", "explain ", "tell me about ", "define ", "suggest ", "recommend ")
    )
    if is_question:
        for terms, answer in DEMO_FAQ:
            if any(term in q for term in terms):
                return answer
        for terms, answer in ENGINEERING_FAQ:
            if any(term in q for term in terms):
                return answer
    engineering_terms = (
        "engineering", "engineer", "mechanical", "civil engineering",
        "electrical engineering", "electronics engineering", "computer engineering",
        "chemical engineering", "biomedical engineering",
    )
    if any(term in q for term in engineering_terms):
        return (
            "🛠️ **Welcome to the Engineering learning path!**\n\n"
            "Engineering uses science, mathematics, and design to solve practical problems. "
            "Different fields focus on different systems and materials.\n\n"
            "**Beginner roadmap**\n"
            "1. Strengthen mathematics, physics, and problem-solving fundamentals\n"
            "2. Practise sketching, measurement, and explaining a design\n"
            "3. Explore fields such as mechanical, civil, electrical, computer, chemical, and biomedical engineering\n"
            "4. Build a small, safe project and test how well it works\n"
            "5. Learn how safety, cost, accessibility, and sustainability affect engineering decisions\n\n"
            "Which field would you like to explore: mechanical, civil, electrical, or computer engineering?"
        )
    if any(term in q for term in ("compare", "both", "difference", "which course", "work together", "learning path")):
        return (
            "Great question! ☁️ **Cloud Computing** teaches you how to use computing services over the internet—"
            "for example, running a server on AWS or storing files in S3.\n\n"
            "⚙️ **DevOps** teaches you how to build, test, release, and operate software reliably using tools such as Git, "
            "Docker, CI/CD, and Terraform.\n\n"
            "A good beginner order is: Linux and Git basics → Cloud fundamentals → a small AWS project → Docker and CI/CD. "
            "You can learn both together through projects.\n\nWould you like to start with Cloud Computing or DevOps?"
        )
    if any(term in q for term in ("devops", "docker", "kubernetes", "ci/cd", "pipeline", "terraform", "ansible")):
        return (
            "⚙️ **Welcome to the DevOps learning path!**\n\n"
            "DevOps brings development and operations teams together so software can be delivered safely and frequently.\n\n"
            "**Beginner roadmap**\n"
            "1. Linux commands and basic networking\n"
            "2. Git and GitHub for version control\n"
            "3. Bash/Python scripting basics\n"
            "4. CI/CD pipelines to automate build and test steps\n"
            "5. Docker containers, then Kubernetes fundamentals\n"
            "6. Terraform for infrastructure as code and Ansible for configuration\n\n"
            "**Hands-on project:** put a small Python app in GitHub, build a Docker image, and automate testing. "
            "Would you like to begin with Git, Docker, or CI/CD?"
        )
    if any(term in q for term in ("cloud", "aws", "ec2", "s3", "compute", "storage", "server", "hosting")):
        return (
            "☁️ **Welcome to the Cloud Computing learning path!**\n\n"
            "Cloud computing lets you use computing resources over the internet instead of buying and maintaining every server yourself.\n\n"
            "**Beginner roadmap**\n"
            "1. Learn IaaS, PaaS, and SaaS\n"
            "2. Explore AWS Regions and Availability Zones\n"
            "3. Learn IAM permissions and shared-responsibility basics\n"
            "4. Practise with EC2 (virtual servers) and S3 (object storage)\n"
            "5. Learn basic networking, monitoring, and cost controls\n\n"
            "**Hands-on project:** host a simple website or deploy a Python app. Start small, use budget alerts, and remove resources after practice. "
            "Would you like to explore EC2, S3, or the overall roadmap first?"
        )
    return (
        "I'm Friday, your learning buddy! In this local preview, I can guide you through Cloud Computing, AWS basics, "
        "DevOps, Engineering, Git, Docker, CI/CD, Kubernetes, Terraform, and beginner projects.\n\n"
        "Try asking: **'Show me the Cloud Computing roadmap'**, **'How do I start learning DevOps?'**, or **'What is computer engineering?'**\n\n"
        "This is a guided demo reply. To enable open-ended AI answers, switch off demo mode and configure Amazon Bedrock as described in the beginner guide."
    )


@application.get("/")
def home():
    return render_template("index.html", demo_mode=DEMO_MODE)


@application.get("/health")
def health():
    return jsonify({"status": "ok", "application": "edutechx-course-chatbot", "mode": "demo" if DEMO_MODE else "bedrock"})


@application.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    raw_messages = payload.get("messages", [])

    if not isinstance(raw_messages, list) or not raw_messages:
        return jsonify({"error": "Send at least one message."}), 400

    # Validate and cap chat history to limit accidental oversized requests.
    messages = []
    for item in raw_messages[-10:]:
        if not isinstance(item, dict):
            continue
        role, content = item.get("role"), item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        content = content.strip()
        if content and len(content) <= 2000:
            messages.append({"role": role, "content": content})

    if not messages or messages[0]["role"] != "user" or messages[-1]["role"] != "user":
        return jsonify({"error": "Conversation history is invalid. Please start a new chat."}), 400
    for previous, current in zip(messages, messages[1:]):
        if previous["role"] == current["role"]:
            return jsonify({"error": "Conversation history is invalid. Please start a new chat."}), 400

    static_reply = static_conversation_reply(messages[-1]["content"])
    if static_reply:
        return jsonify({"reply": static_reply, "mode": "static"})

    if DEMO_MODE:
        return jsonify({"reply": demo_reply(messages[-1]["content"]), "mode": "demo"})

    bedrock_messages = [
        {"role": item["role"], "content": [{"text": item["content"]}]}
        for item in messages
    ]
    try:
        response = get_bedrock_client().converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=bedrock_messages,
            inferenceConfig={"maxTokens": 700, "temperature": 0.5, "topP": 0.9},
        )
        blocks = response.get("output", {}).get("message", {}).get("content", [])
        reply = "\n".join(block["text"] for block in blocks if isinstance(block, dict) and "text" in block).strip()
        if not reply:
            logger.warning("Bedrock returned an empty response")
            return jsonify({"error": "The AI returned an empty response. Please try again."}), 502
        return jsonify({"reply": reply, "mode": "bedrock"})
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Amazon Bedrock request failed: %s", exc)
        return jsonify({
            "error": "The AI service could not answer. Check the AWS Region, model availability, IAM permission "
                     "bedrock:InvokeModel, and model access, then try again."
        }), 502
    except Exception:
        logger.exception("Unexpected chatbot error")
        return jsonify({"error": "An unexpected server error occurred. Check the server logs."}), 500


if __name__ == "__main__":
    # Development only. Gunicorn runs the app on Elastic Beanstalk.
    application.run(host="127.0.0.1", port=5000, debug=False)
