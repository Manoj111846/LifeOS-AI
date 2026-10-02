# LifeOS AI 🧠

> Your information has connections. We make them actionable.

LifeOS AI is a personal intelligence dashboard that connects goals, projects, tasks, deadlines and documents into a contextual workspace.

## Current MVP

- User registration and login
- Dashboard with live counts
- Goals
- Projects
- Tasks and dependencies
- Document upload
- Interactive knowledge graph
- Context-aware assistant
- Scenario simulator
- Health endpoint for deployment checks
- Docker/Gunicorn deployment support

## Run locally

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

http://127.0.0.1:5000

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Production

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

A reverse proxy such as Nginx can expose the service on ports 80/443.

## AWS

The application is designed to be deployable on AWS EC2 or another AWS hosting service. Record only the AWS services actually used in the final deployment.

The hackathon also requires documented proof of the coding-agent connection to the AWS console and a publicly reachable live application. See the official Zero to Shipped rules:
https://builder.aws.com/build/hackathons/e83e84e5-4f4c-383b-bbe9-4a15ac195d55/zero-to-shipped?tab=rules

## Important

Do not commit `.env`, passwords, API keys, or other secrets.

This repository is an original LifeOS AI implementation for the hackathon project. Before final submission, verify that the project has not previously been published.
