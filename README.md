# 🤖 AI Task Planner

An intelligent task planning system powered by AI that combines a Telegram bot, web dashboard, and FastAPI backend to help users break down complex tasks into manageable steps and track their progress.

---

## 📖 Overview

**AI Task Planner** is a comprehensive task management solution that leverages artificial intelligence to help users:

- 🎯 **Create tasks** using a Telegram bot interface
- 🤖 **Generate task steps** automatically using AI (OpenAI/Claude)
- 📊 **Track progress** through an intuitive web dashboard
- ⏱️ **Estimate time** for each task and subtask
- 🔐 **Secure authentication** across all platforms

The system operates in parallel with a Telegram bot for quick task input and a web interface for detailed planning and monitoring.

---

## ✨ Features

- 🚀 **Dual Interface**: Telegram bot for quick access + web dashboard for detailed management
- 🧠 **AI-Powered Task Breakdown**: Automatically generate task steps using OpenAI or Claude API
- 📱 **Real-time Updates**: Async operations ensure smooth performance
- 🔐 **Secure Authentication**: Token-based user authentication
- 💾 **Persistent Storage**: SQLite database with SQLAlchemy ORM
- ⏰ **Time Tracking**: Estimate and monitor time spent on tasks
- 📈 **Progress Monitoring**: Visual dashboard with task completion statistics
- 🎨 **Modern UI**: Responsive HTML/CSS/JavaScript frontend

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Bot Framework** | python-telegram-bot (aiogram) |
| **AI API** | OpenAI / Claude API |
| **Web Backend** | FastAPI |
| **Database** | SQLite + SQLAlchemy |
| **Frontend** | HTML + CSS + JavaScript |
| **Async Runtime** | asyncio |
| **Server** | Uvicorn |
| **Language** | Python 3.8+ |

---

## 📁 Project Structure

```text
AI_TASK_PLANNER/
│
├── main.py
├── Tech_stack.txt
├── .gitignore
│
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── handlers.py
│   ├── states.py
│   │
│   └── ai/
│       ├── __init__.py
│       └── generate.py
│
├── core/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   ├── repository.py
│   ├── auth.py
│   └── users.py
│
└── site_F/
    ├── __init__.py
    ├── main.py
    │
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── settings.html
    │   └── index.html
    │
    └── static/
        ├── css/
        │   └── style.css
        ├── image/
        │   └── image.png
        └── js/
            ├── app.js
            └── style.js
```


---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **pip** (Python package manager)
- **API Keys** for:
  - Telegram Bot Token (from [@BotFather](https://t.me/botfather))
  - OpenAI API Key or Claude API Key

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mentuly/AI_TASK_PLANNER.git
cd AI_TASK_PLANNER
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create a \`.env\` file in the root directory:

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token_here

# AI API (choose one)

**I would recommend using the OpenAI API.**

OPENAI_API_KEY=your_openai_api_key

# or
CLAUDE_API_KEY=your_claude_api_key

# Bot_id:

@AI_task_planer_bot

# Database
DATABASE_URL=sqlite:///./tasks.db

# Web Server
API_HOST=127.0.0.1
API_PORT=8000
```

### 2. Database Setup

The database is initialized automatically when the application starts. The \`init_db()\` function creates all necessary tables.

---

## ▶️ Running the Application

### Start the Application

```bash
python main.py
```

This will:
1. Initialize the database
2. Start the Telegram bot (polling mode)
3. Start the FastAPI web server on \`http://127.0.0.1:8000\`

### Access the Application

- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Telegram Bot**: Message your bot on Telegram

---

## 📚 API Documentation

### Main Endpoints

#### Home Page
```http
GET /
```
Returns the home page.

#### Login
```http
GET /login
```
Displays the login page.

#### Dashboard
```http
GET /dashboard
```
Displays the user's tasks dashboard (requires authentication).

#### Get Tasks (API)
```http
GET /tasks
```
Returns JSON list of user's tasks with steps and time estimates.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Build Website",
    "is_done": false,
    "total_minutes": 480,
    "steps": [
      {
        "title": "Design Mockups",
        "description": "Create UI/UX designs",
        "minutes": 120,
        "is_done": false
      }
    ]
  }
]
```

#### Mark Task as Done
```http
POST /done/{task_id}
```
Marks a task as completed.

#### Authentication
```http
GET /auth/{token}
```
Authenticates user with token and sets session cookie.

---

## 💡 Usage

### Via Telegram Bot

1. Start the bot, by user @AI_task_planer_bot and press \`/start\`
2. Send a task description
3. The bot will use AI to break it down into steps
4. Track your progress directly from Telegram

### Via Web Dashboard

1. Navigate to [http://localhost:8000](http://localhost:8000)
2. Log in with your credentials
3. View all your tasks and their progress
4. Mark tasks as complete
5. Access settings for account management

---

## 🔧 Development

### Adding New Features

1. Create a new branch: \`git checkout -b feature/your-feature\`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages
5. Push and create a pull request

### Project Guidelines

- Follow **PEP 8** style guide for Python code
- Use **type hints** for better code clarity
- Write **docstrings** for functions and classes
- Keep functions small and focused
- Test changes before committing

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

Please ensure:
- Code follows the project's style guide
- Changes are well-documented
- Tests pass (if applicable)
- Commit messages are clear and descriptive

---

## 📜 License

This project is open source and available under the MIT License. See the \`LICENSE\` file for more information.

---

## 📞 Contact

For questions, issues, or suggestions:

- **GitHub Issues**: [Create an issue](https://github.com/mentuly/AI_TASK_PLANNER/issues)
- **My contact**: [My e-mail](danlutsencko@gmail.com)
---

## 🙏 Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram bot library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [OpenAI](https://openai.com/) - AI API
- All contributors and users of this project

---

**Made by [mentuly](https://github.com/mentuly)**