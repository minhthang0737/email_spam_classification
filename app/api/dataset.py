from datetime import datetime
import csv
import gzip
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file

from app import db
from app.models.email_dataset import EmailDataset
from app.utils.logger import get_logger
from app.auth import login_required

logger = get_logger(__name__)

dataset_bp = Blueprint(
    "dataset",
    __name__,
    url_prefix="/api/dataset"
)


@dataset_bp.get("")
@login_required("admin")
def get_dataset():
    logger.info("Fetching dataset list")
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 50, type=int), 1), 200)
    query = EmailDataset.query
    label = request.args.get("label", "ALL").upper()
    search = request.args.get("search", "").strip()[:200]
    if label in ("SPAM", "NOT_SPAM"):
        query = query.filter(EmailDataset.label == label)
    if search:
        query = query.filter(EmailDataset.email_content.ilike(f"%{search}%"))
    total = query.count()
    spam_count = EmailDataset.query.filter_by(label="SPAM").count()
    safe_count = EmailDataset.query.filter_by(label="NOT_SPAM").count()
    datasets = (
        query
        .order_by(EmailDataset.id.desc())
        .offset((page - 1) * per_page).limit(per_page).all()
    )

    return jsonify({
        "data": [
            dataset.to_dict()
            for dataset in datasets
        ],
        "pagination": {"page": page, "perPage": per_page, "total": total,
                       "pages": (total + per_page - 1) // per_page,
                       "spam": spam_count, "notSpam": safe_count}
    }), 200


@dataset_bp.post("/seed-large")
@login_required("admin")
def seed_large_dataset():
    seed_file = Path(current_app.config.get(
        "DEMO_EMAIL_SEED_FILE",
        Path(__file__).resolve().parents[2] / "data" / "demo_emails_100k.csv.gz",
    ))
    if not seed_file.is_file():
        return jsonify({"message": "Không tìm thấy file seed 100k. Hãy chạy scripts/generate_demo_emails.py."}), 503

    known = {content for (content,) in db.session.query(EmailDataset.email_content).all()}
    added = skipped = 0
    batch = []
    try:
        with gzip.open(seed_file, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["email", "label"]:
                return jsonify({"message": "File seed có cấu trúc không hợp lệ."}), 500
            for item in reader:
                content = item["email"].strip()
                label = item["label"].strip().upper()
                if not content or label not in ("SPAM", "NOT_SPAM"):
                    continue
                if content in known:
                    skipped += 1
                    continue
                known.add(content)
                batch.append(EmailDataset(email_content=content, label=label))
                if len(batch) >= 1000:
                    db.session.add_all(batch)
                    db.session.flush()
                    added += len(batch)
                    batch.clear()
        if batch:
            db.session.add_all(batch)
            db.session.flush()
            added += len(batch)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Large demo dataset import failed")
        return jsonify({"message": "Không thể nạp bộ dữ liệu demo."}), 500
    return jsonify({"message": f"Đã nạp {added:,} email; bỏ qua {skipped:,} email đã tồn tại.",
                    "added": added, "skipped": skipped,
                    "total": EmailDataset.query.count()}), 200


@dataset_bp.get("/seed-file")
@login_required("admin")
def download_large_seed():
    seed_file = Path(current_app.config.get(
        "DEMO_EMAIL_SEED_FILE",
        Path(__file__).resolve().parents[2] / "data" / "demo_emails_100k.csv.gz",
    ))
    if not seed_file.is_file():
        return jsonify({"message": "Chưa tạo file seed 100k."}), 404
    return send_file(seed_file, as_attachment=True, download_name="demo_emails_100k.csv.gz")


@dataset_bp.post("")
@login_required("admin")
def create_dataset():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body cannot be empty."
        }), 400

    email_content = data.get("email")
    label = data.get("label")

    if not email_content or not email_content.strip():
        return jsonify({
            "message": "Email content cannot be empty."
        }), 400

    if not label:
        return jsonify({
            "message": "Label cannot be empty."
        }), 400

    label = label.strip().upper()

    if label not in ("SPAM", "NOT_SPAM"):
        return jsonify({
            "message": "Label must be SPAM or NOT_SPAM."
        }), 400

    dataset = EmailDataset(
        email_content=email_content.strip(),
        label=label
    )

    db.session.add(dataset)
    db.session.commit()

    return jsonify(dataset.to_dict()), 201


@dataset_bp.put("/<int:dataset_id>")
@login_required("admin")
def update_dataset(dataset_id):
    dataset = db.session.get(
        EmailDataset,
        dataset_id
    )

    if dataset is None:
        return jsonify({
            "message": "Dataset not found."
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body cannot be empty."
        }), 400

    if "email" in data:
        email_content = data.get("email")

        if not email_content or not email_content.strip():
            return jsonify({
                "message": "Email content cannot be empty."
            }), 400

        dataset.email_content = email_content.strip()

    if "label" in data:
        label = data.get("label")

        if not label:
            return jsonify({
                "message": "Label cannot be empty."
            }), 400

        label = label.strip().upper()

        if label not in ("SPAM", "NOT_SPAM"):
            return jsonify({
                "message": "Label must be SPAM or NOT_SPAM."
            }), 400

        dataset.label = label

    dataset.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(dataset.to_dict()), 200


@dataset_bp.delete("/<int:dataset_id>")
@login_required("admin")
def delete_dataset(dataset_id):
    dataset = db.session.get(
        EmailDataset,
        dataset_id
    )

    if dataset is None:
        return jsonify({
            "message": "Dataset not found."
        }), 404

    db.session.delete(dataset)
    db.session.commit()

    return jsonify({
        "message": "Dataset deleted successfully."
    }), 200
