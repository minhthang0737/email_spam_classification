# Email Spam Classification System

Backend foundation for the Email Spam Classification System.

## Scope of TASK-001

- Python project initialization
- Flask backend
- Dependency definition in `requirements.txt`
- Configuration
- Package structure for API, models, services, ML and saved models
- Basic health-check endpoint

## Project structure

```text
email_spam_classification/
├── app/
│   ├── api/
│   ├── ml/
│   ├── models/
│   ├── services/
│   ├── __init__.py
│   └── config.py
├── saved_models/
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Run

### 1. Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and update the PostgreSQL connection when needed.

### 4. Start Flask

```bash
python run.py
```

Health check:

```text
GET /api/health
```

Expected response:

```json
{
  "service": "Email Spam Classification API",
  "status": "UP"
}
```

## Note

Database tables and business APIs are intentionally not implemented in TASK-001.
They belong to subsequent backlog tasks.
