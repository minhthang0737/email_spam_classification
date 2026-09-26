# Email Spam Classification System

Web application for classifying email text as **SPAM** or **NOT_SPAM** using Flask, PostgreSQL, and scikit-learn (TF-IDF + MultinomialNB).

## Hướng dẫn demo: đăng nhập và import data

### Chạy lần đầu bằng Docker

Trong thư mục dự án, mở terminal và chạy:

```powershell
docker compose up -d --build
docker compose exec app python scripts/create_admin.py
```

Nếu dùng Python local đã cài dependencies và cấu hình `.env`, chạy:

```powershell
python scripts/init_db.py
python scripts/create_admin.py
python run.py
```

Mở [trang đăng nhập](http://127.0.0.1:5000/login), dùng **admin / Admin123!** nếu chưa cấu hình `ADMIN_USERNAME` và `ADMIN_PASSWORD`. Script tạo admin không đổi mật khẩu tài khoản đã tồn tại. Nếu đã đổi mật khẩu, dùng mật khẩu mới.

### Nạp dữ liệu cho mọi bảng

1. Đăng nhập Admin, chọn **Thiết lập** trên menu.
2. Trong **Nạp dữ liệu demo toàn hệ thống**, bấm **Nhập data cho mọi bảng** và chờ thông báo hoàn tất.
3. Kiểm tra **Dataset**, **Lịch sử**, **Tài khoản**, **Chặn IP / domain** và **Mô hình**. Lần nạp đầu thêm 100.000 email huấn luyện tổng hợp, 100 dòng lịch sử demo, một tài khoản Analyst, hai IP mẫu, hai domain mẫu và một bản ghi model chưa huấn luyện. Tổng số có thể lớn hơn nếu DB đã có dữ liệu.
4. Vào **Mô hình**, bấm **Huấn Luyện Lại (Train Model)** và chờ hoàn tất; sau đó dùng **Phân loại**. Seed không tự train hoặc thay model đang hoạt động. Bản ghi model placeholder không dùng để dự đoán.

Bộ seed `data/demo_emails_100k.csv.gz` đã đi cùng repository, không cần tải riêng hay giải nén. Bấm nạp lại sẽ bỏ qua mẫu đã có. Lịch sử có tiền tố `[DEMO SEED]` là dữ liệu giả lập để trình diễn, không phải kết quả đánh giá model.

Chỉ cần thêm email huấn luyện: vào **Dataset → Tạo thêm 100.000 email demo**. Nút **Tải file seed** tải bộ CSV.gz; chức năng import hiện nạp bộ seed đóng gói, chưa hỗ trợ upload CSV bất kỳ. Nếu file seed bị thiếu, tạo lại bằng `python scripts/generate_demo_emails.py` (Docker: `docker compose exec app python scripts/generate_demo_emails.py`).

Sau lần seed đầu, có thể đăng nhập bằng **demo.analyst / DemoAnalyst123!** để thử vai trò Analyst. Tài khoản này xem/xóa lịch sử, gửi nhãn sửa và cập nhật hồ sơ; các chức năng quản trị cần Admin. Seed lại không đặt lại mật khẩu tài khoản đã tồn tại.

Trong **Thiết lập**, dùng **Hồ sơ** để sửa tên hiển thị/email hoặc **Đổi mật khẩu** để nhập mật khẩu hiện tại, mật khẩu mới tối thiểu 8 ký tự và xác nhận. Sau khi cập nhật code, khởi động lại server local hoặc chạy `docker compose up -d --build` để hiện menu và chức năng mới.

## Features

- Public: classify email
- Analyst: sign in, review/delete history and submit corrected labels
- Admin: manage training dataset, user roles, IP/domain blocklists, train/retrain model and compare algorithms
- Email indicator checker: find literal IPs and sender/link domains in email text and compare them to internal blocklists
- One-click 100,000-row synthetic email seed; compressed CSV can also be downloaded and re-imported idempotently
- Bootstrap 4.6 interface with a restrained, conventional admin layout
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

Create the first administrator after the app starts:

```powershell
docker compose exec app python scripts/create_admin.py
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
- PostgreSQL is available to the app inside Docker at `db:5432`; the Compose file does not publish a database port on the host.

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

### Demo account, data, and administration

Before signing in, run `python scripts/create_admin.py`. The demo defaults to `admin` / `Admin123!`; set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `SECRET_KEY` in `.env` before using a non-demo deployment. Existing accounts are not reset by this script.

Run `python scripts/seed_dataset.py` to add a repeatable set of 318 examples (18 hand-written and 300 generated English/Vietnamese samples). It adds only content not already present. These records are for demonstrations and CRUD/training flows, not for real-world performance claims.

To generate or refresh the larger reproducible seed file, run `python scripts/generate_demo_emails.py`. It creates `data/demo_emails_100k.csv.gz`, a balanced set of exactly 100,000 synthetic email messages (50,000 SPAM and 50,000 NOT_SPAM). Admins can click **Tạo thêm 100.000 email demo** on `/admin/dataset`; rows already present are skipped, and the paginated table stays responsive. The file is also downloadable on that page. These are generated examples, not real email traffic. Importing them does not send mail or automatically train the active model. Retraining on 100,000 examples may take longer and the synthetic set is for application demos only.

- `/login`: analysts can view history and submit corrected labels; administrators manage the dataset, accounts, models, and IP blocklist.
- `/admin/users`: administrator-only account creation, activation, role changes, and deletion; the last active administrator cannot be demoted or removed.
- `/settings`: each signed-in user can edit their display name/email and change their password after verifying the current password. Admins can import an idempotent whole-project demo seed from this page.
- `/admin/ip`: find literal IPs and sender/link domains in email text; maintain CRUD lists for blocked IPs and domains. Domain matching is exact and does not automatically include subdomains. The checker does not query DNS or external reputation services.
- `/admin/dataset` has create/read/update/delete for training samples; `/history` includes search, filtering, deletion, and feedback.
- The interface uses Bootstrap 4.6 and a restrained, conventional stylesheet.

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Classify email |
| GET | `/api/classifications` | List history |
| GET | `/api/classifications/{id}` | History detail |
| DELETE | `/api/classifications/{id}` | Delete history |
| POST | `/api/classifications/{id}/feedback` | Correct a label and update the training dataset |
| GET/POST | `/api/users` | Admin-only account list/create |
| PUT/DELETE | `/api/users/{id}` | Admin-only account update/delete |
| POST | `/api/ip/check` | Check literal IP addresses in supplied email text |
| GET/POST | `/api/ip/blocklist` | Admin-only internal IP blocklist list/add |
| PUT/DELETE | `/api/ip/blocklist/{id}` | Admin-only blocklist update/delete |
| GET/POST | `/api/ip/domain-blocklist` | Admin-only internal domain blocklist list/add |
| PUT/DELETE | `/api/ip/domain-blocklist/{id}` | Admin-only domain blocklist update/delete |
| PUT | `/api/account/profile` | Update the signed-in user's display name and email |
| PUT | `/api/account/password` | Change password after checking the current password |
| POST | `/api/demo/seed` | Admin-only idempotent seed for dataset, history, demo analyst, IP/domain lists and model metadata |
| GET/POST | `/api/dataset` | List/add dataset |
| POST | `/api/dataset/seed-large` | Idempotently import the 100,000-row compressed demo seed |
| GET | `/api/dataset/seed-file` | Download the compressed synthetic seed file |
| PUT/DELETE | `/api/dataset/{id}` | Update/delete dataset |
| POST | `/api/model/train` | Train model |
| POST | `/api/model/compare` | Compare MultinomialNB and LogisticRegression on the same holdout |
| GET | `/api/model` | Active model info |

Classification feedback accepts `{ "label": "SPAM" }` or `{ "label": "NOT_SPAM" }`. It updates dataset rows with the same exact email text, or adds one when no match exists. Retraining remains a manual action through the Admin Model page. The comparison endpoint evaluates both algorithms without changing the active model.

Text preprocessing preserves Unicode letters and Vietnamese diacritics in both training and prediction. The seed dataset includes a small set of self-authored Vietnamese examples for demonstration; it is not a substitute for a larger labeled corpus.

History, dataset, model, user, and IP administration require sign-in. The default demo credential is `admin` / `Admin123!` unless `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set before running `python scripts/create_admin.py`. Change demo settings and `SECRET_KEY` before deploying.

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
