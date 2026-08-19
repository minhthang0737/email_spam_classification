# Email Spam Classification System

Web application for classifying email text as **SPAM** or **NOT_SPAM** using Flask, PostgreSQL, and scikit-learn (TF-IDF + MultinomialNB).

## Features

- User: classify email, view classification history
- Admin: manage training dataset, train/retrain model, view model metrics
- REST APIs per SRS v1.1
- Simple HTML/JS frontend

## Project structure

```text
email_spam_classification/
├── app/
│   ├── api/          # REST endpoints + HTML views
│   ├── ml/           # preprocessing, trainer, predictor
│   ├── models/       # SQLAlchemy models
│   ├── services/     # business logic
│   ├── static/       # CSS + JS
│   ├── templates/    # HTML pages
│   └── config.py
├── docker/           # entrypoint for Docker
├── scripts/          # init_db, seed_dataset
├── saved_models/     # trained .joblib files
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## Should you use Docker?

**Yes — recommended for this project**, especially when:

- SRS requires **PostgreSQL** and you do not want to install it manually on Windows
- You need **consistent versions** of Python 3.11, PostgreSQL 16, Flask, scikit-learn, numpy, etc.
- You work in a group and everyone should run the **same environment**

Docker Compose runs PostgreSQL + Flask app together with pinned versions in `requirements.txt` and `docker-compose.yml`.

**Use local venv + SQLite** only for quick experiments without PostgreSQL (not aligned with SRS DB requirement).

## Setup with Docker (recommended)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Windows

### 1. Start services

```powershell
cd C:\UserLocal\Desktop\UIT\spam_email
docker compose up --build
```

First run will:

1. Start PostgreSQL 16
2. Build Python 3.11 image and install pinned dependencies
3. Create tables (`scripts/init_db.py`)
4. Seed sample dataset if empty (`scripts/seed_dataset.py`)
5. Start Flask on http://127.0.0.1:5000

### 2. Verify

- App: http://127.0.0.1:5000
- Health: http://127.0.0.1:5000/api/health
- PostgreSQL from host: `localhost:5432` (user `postgres`, password `postgres`, db `email_spam_classification`)

### 3. Useful commands

```powershell
# Stop
docker compose down

# Stop and remove DB volume (reset data)
docker compose down -v

# Run tests inside container
docker compose run --rm app pytest tests/ -v --ignore=tests/test_training_manual.py

# Rebuild after code changes
docker compose up --build
```

### Version pinning

| Component    | Version        | Where defined              |
|-------------|----------------|----------------------------|
| Python      | 3.11           | `Dockerfile`               |
| PostgreSQL  | 16-alpine      | `docker-compose.yml`       |
| Flask, ML…  | pinned         | `requirements.txt`         |

## Setup without Docker (local venv)

### 1. Virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment

Copy `.env.example` to `.env` and update values.

**PostgreSQL (SRS):**

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/email_spam_classification
```

Create database:

```sql
CREATE DATABASE email_spam_classification;
```

**SQLite (quick local dev only):**

```env
DATABASE_URL=sqlite:///email_spam_classification.db
```

### 3. Initialize database and seed data

```powershell
python scripts/init_db.py
python scripts/seed_dataset.py
```

### 4. Run server

```powershell
python run.py
```

Open http://127.0.0.1:5000

Health check: `GET /api/health`

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Classify email |
| GET | `/api/classifications` | List history |
| GET | `/api/classifications/{id}` | History detail |
| DELETE | `/api/classifications/{id}` | Delete history |
| GET/POST | `/api/dataset` | List/add dataset |
| PUT/DELETE | `/api/dataset/{id}` | Update/delete dataset |
| POST | `/api/model/train` | Train model |
| GET | `/api/model` | Active model info |

## Tests

**Local:**

```powershell
pytest tests/ -v --ignore=tests/test_training_manual.py
```

**Docker:**

```powershell
docker compose run --rm app pytest tests/ -v --ignore=tests/test_training_manual.py
```

## Typical workflow

1. Seed dataset (automatic on Docker first start, or Admin Dataset UI)
2. Train model via Admin Model UI or `POST /api/model/train`
3. Classify emails via UI or `POST /api/predict`
4. View history on History page or `GET /api/classifications`

## Note (TASK-001 scope)

Database tables and business APIs are implemented beyond the original TASK-001 scaffold. Use Docker or PostgreSQL per SRS for full functionality.
