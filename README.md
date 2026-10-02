# LifeOS AI 🧠

> **Your information has connections. We make them actionable.**

LifeOS AI is a personal intelligence command center that brings **goals, projects, tasks, deadlines, documents, dependencies, and context** into one connected workspace.

Instead of treating every item as an isolated record, LifeOS AI helps users understand how their information is related and what action should come next.

## 🚀 Live Demo

**HTTPS demo:**

https://lance-alto-regard-chips.trycloudflare.com

> The HTTPS URL is a temporary Cloudflare Quick Tunnel forwarding to the LifeOS AI application running on an AWS EC2 instance. The underlying application is hosted on AWS.

**GitHub:**

https://github.com/Manoj111846/LifeOS-AI

---

## 📸 Screenshots

### Landing Page

![LifeOS AI Landing Page](screenshots/landing-page.png)

### Personal Dashboard

![LifeOS AI Dashboard](screenshots/dashboard.png)

The dashboard brings together goals, projects, pending tasks, documents, priorities, and the user's current context in one view.

---

## ✨ Features

### 🧠 Personal Knowledge Graph

Connect goals, projects, tasks, deadlines, documents, and dependencies into a connected information structure.

### 🎯 Smart Planning

Create goals, projects, and tasks with priorities, deadlines, completion status, and relationships.

### 🔗 Task Dependencies

Represent dependencies between tasks so users can understand what needs to happen before another action can be completed.

### 📄 Document Management

Upload documents and keep them alongside the user's personal goals, projects, and tasks.

### 🤖 Context-Aware Assistant

Ask questions about the information stored in LifeOS AI. The current MVP uses application context and rule-based reasoning rather than an external large language model.

### 🔮 Scenario Simulator

Explore hypothetical changes to tasks and priorities and see contextual effects using the available project and dependency information.

### 📊 Personal Dashboard

View active goals, projects, pending tasks, priority tasks, deadlines, and documents from a centralized dashboard.

### ❤️ Health Endpoint

The application exposes `/api/health` for deployment and container health checks.

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      User Browser    │
                    └──────────┬───────────┘
                               │ HTTPS
                               ▼
                    ┌──────────────────────┐
                    │  Cloudflare Quick     │
                    │      Tunnel           │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │        Amazon EC2              │
              │                                │
              │  ┌──────────────────────────┐  │
              │  │    Docker Container      │  │
              │  │      LifeOS AI           │  │
              │  │ Flask + Gunicorn         │  │
              │  └────────────┬─────────────┘  │
              │               │                 │
              │          SQLite DB              │
              └────────────────────────────────┘
                               ▲
                               │ Docker image
                               │
                    ┌──────────┴───────────┐
                    │    Amazon ECR         │
                    │   lifeos-ai:latest   │
                    └──────────────────────┘
```

---

## ☁️ AWS Services Used

### Amazon EC2

Hosts the running LifeOS AI application in a Docker container and provides the AWS compute environment.

### Amazon ECR

Stores the LifeOS AI Docker image. The image is pushed to ECR and pulled by the EC2 instance during deployment.

Repository:

```text
995342110829.dkr.ecr.ap-south-1.amazonaws.com/lifeos-ai
```

### AWS IAM

An IAM role is attached to the EC2 instance so it can authenticate with AWS services and pull the private ECR image without storing long-lived AWS access keys on the server.

### Docker

The Flask application is packaged as a Docker image and deployed on EC2 using Gunicorn.

---

## 🤖 Coding Agent & AWS Development

LifeOS AI was developed with assistance from **Cline**, an AI coding agent connected to AWS through the **AWS Agent Toolkit / AWS MCP Server**.

The coding-agent workflow was used during development to:

- Inspect the application structure
- Review deployment requirements
- Configure the AWS development workflow
- Work with AWS resources
- Prepare the application for Docker deployment
- Support the AWS deployment process

The AWS connection was verified through the AWS Agent Toolkit by successfully querying AWS environment information.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Frontend | HTML / CSS / JavaScript |
| Database | SQLite |
| Visualization | D3.js |
| Application Server | Gunicorn |
| Containerization | Docker |
| Cloud Compute | Amazon EC2 |
| Container Registry | Amazon ECR |
| Access Control | AWS IAM |
| Coding Agent | Cline |
| AWS Agent Connection | AWS Agent Toolkit / AWS MCP Server |

---

## 📁 Project Structure

```text
LifeOS-AI/
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .env.example
├── .gitignore
├── .dockerignore
├── uploads/
├── screenshots/
│   ├── landing-page.png
│   └── dashboard.png
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── goals.html
│   ├── projects.html
│   ├── tasks.html
│   ├── documents.html
│   ├── graph.html
│   ├── assistant.html
│   └── scenario.html
└── static/
    ├── style.css
    └── app.js
```

---

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Manoj111846/LifeOS-AI.git
cd LifeOS-AI
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 🐳 Run with Docker

Build the image:

```bash
docker build -t lifeos-ai:latest .
```

Run the container:

```bash
docker run -d --name lifeos-ai -p 5000:5000 lifeos-ai:latest
```

Open:

```text
http://127.0.0.1:5000
```

---

## 🚢 AWS Deployment Flow

```text
Local LifeOS AI
      │
      ▼
Docker Build
      │
      ▼
Amazon ECR
      │
      ▼
Amazon EC2
      │
      ▼
Docker Container
      │
      ▼
Public Application
```

The deployed container runs Gunicorn and maps the application's port to the EC2 instance's public HTTP endpoint.

---

## 🔐 Security Notes

- Do not commit `.env` files.
- Do not commit AWS access keys, passwords, API keys, or other secrets.
- The repository uses `.gitignore` and `.dockerignore` to help prevent sensitive/local files from being committed.
- The EC2 deployment uses an IAM role for AWS access instead of storing long-lived AWS credentials on the server.

---

## 🎯 Hackathon Submission

LifeOS AI was built for the **AWS Zero to Shipped Hackathon 2026**.

- **App category:** Daily Life Enhancement
- **Focus track:** Startup
- **AWS deployment:** Amazon EC2
- **Container registry:** Amazon ECR
- **Coding agent:** Cline
- **AWS agent connection:** AWS Agent Toolkit / AWS MCP Server
- **Live application:** Public HTTPS endpoint

The official hackathon requires a live application running on AWS, a publicly reachable URL, documented coding-agent connection, an app category and focus track, and documentation of AWS services and coding-agent usage. citeturn0search1turn0search4

Official rules:
https://builder.aws.com/build/hackathons/e83e84e5-4f4c-383b-bbe9-4a15ac195d55/zero-to-shipped?tab=rules

---

## 🔮 Future Enhancements

- AWS-native durable database storage
- Amazon S3 document storage
- Calendar integration
- Email context
- GitHub integration
- Voice interaction
- Mobile application
- Advanced knowledge graph capabilities
- Long-term personal context
- Autonomous task workflows
- Advanced AI model integration

---

## 👨‍💻 Project

**LifeOS AI**

Built by **Manoj Kommu**.

> Don't just store information. Understand how it connects. Turn those connections into action.
