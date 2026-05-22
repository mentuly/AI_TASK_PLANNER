# AI Task Planner

AI Task Planner is a task management application with a Telegram bot and a web dashboard. It helps users create tasks, generate step-by-step plans, and track progress using async FastAPI and AI-powered task breakdown.

---

## Overview

This repository contains two main services:

- Telegram bot for task creation and planning via aiogram
- Web dashboard for viewing tasks, steps, and completion status via FastAPI

Both services use a shared SQLite database and are ready for local execution or Docker deployment with docker-compose.

---

## Features

- Telegram bot for fast task creation
- AI-powered task step generation
- Web dashboard for task tracking
- Token-based authentication for web access
- SQLite storage for persistent data
- Docker-ready configuration with Dockerfile and docker-compose.yml
- Docker secrets support for BOT_TOKEN

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Bot | aiogram |
| Web | FastAPI |
| DB | SQLite |
| AI API | OpenAI / Claude |
| Server | Uvicorn |
| Language | Python 3.12 |
| Orchestration | docker-compose |

---

## Project Structure

```text
AI_TASK_PLANNER/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── .secrets/
│   └── bot_token.example
├── main.py
├── requirements.txt
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── handlers.py
│   ├── states.py
│   └── ai/
│       ├── __init__.py
│       └── generate.py
├── core/
│   ├── __init__.py
│   ├── auth.py
│   ├── db.py
│   ├── models.py
│   ├── repository.py
│   └── users.py
└── site_F/
    ├── __init__.py
    ├── main.py
    ├── static/
    └── templates/
        ├── base.html
        ├── dashboard.html
        ├── home.html
        ├── login.html
        └── settings.html
```

---

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Telegram Bot Token
- OpenAI or Claude API key for task generation

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mentuly/AI_TASK_PLANNER.git
dcd AI_TASK_PLANNER
```

### 2. Create a virtual environment (optional)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### Local environment variables

Copy `.env.example` to `.env` and add your values:

```env
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key
# or
# CLAUDE_API_KEY=your_claude_api_key
DB_NAME=tasks.db
```

### Docker secrets

Docker uses a secret file for BOT_TOKEN.

Create the local secret file:

```bash
mkdir -p .secrets
copy .secrets\bot_token.example .secrets\bot_token
```

Then paste your bot token into `.secrets/bot_token`.

---

## Running the application

### Local

```bash
python main.py
```

This starts:
- Telegram bot
- FastAPI site at http://localhost:8000

### Docker

Run only the site:

```bash
docker compose up --build site
```

Run only the bot:

```bash
docker compose up --build bot
```

Run both services:

```bash
docker compose up --build
```

---

## Access

- Web interface: http://localhost:8000
- Telegram bot: your bot created via BotFather

---

## Database

- SQLite database path is set by DB_NAME
- In Docker, the default database file is `./data/tasks.db`
- The database is initialized automatically at startup

---

## API Endpoints

- `GET /` — home page
- `GET /login` — login page
- `GET /dashboard` — dashboard page (requires auth)
- `GET /tasks` — returns tasks as JSON
- `POST /done/{task_id}` — mark a task done
- `GET /auth/{token}` — authenticate user by token

---

## Notes

- Use Docker Compose with secrets for production-like deployment
- Do not commit real tokens to Git
- `.gitignore` already excludes `.env` and `.secrets`