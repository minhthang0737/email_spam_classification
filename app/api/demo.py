from flask import Blueprint, jsonify

from app import db
from app.api.dataset import seed_large_dataset
from app.auth import login_required
from app.models.email_classification import EmailClassification
from app.models.ip_reputation import BlockedDomain, BlockedIP
from app.models.model_information import ModelInformation
from app.models.user import User


demo_bp = Blueprint("demo", __name__, url_prefix="/api/demo")


@demo_bp.post("/seed")
@login_required("admin")
def seed_all_demo_data():
    dataset_response, status = seed_large_dataset()
    if status != 200:
        return dataset_response, status
    dataset_result = dataset_response.get_json()

    added = {"dataset": dataset_result["added"], "history": 0, "users": 0,
             "ipBlocklist": 0, "domainBlocklist": 0, "modelInformation": 0}

    history_templates = [
        ("SPAM", "Thông báo trúng thưởng! Xác nhận quà tại https://claim-prize.test/item/{:03d}"),
        ("NOT_SPAM", "Nhóm xác nhận lịch họp đồ án lúc 10 giờ, nội dung mã tham khảo {:03d}."),
    ]
    version = (ModelInformation.query.filter_by(is_active=True).order_by(
        ModelInformation.trained_at.desc()).first())
    model_version = version.model_version if version else "DEMO-SEED-NOT-TRAINED"
    existing_history = {content for (content,) in db.session.query(
        EmailClassification.email_content).filter(
            EmailClassification.email_content.like("[DEMO SEED]%")
        ).all()}
    for index in range(100):
        label, template = history_templates[index % 2]
        content = f"[DEMO SEED] {template.format(index + 1)}"
        if content in existing_history:
            continue
        existing_history.add(content)
        confidence = 0.91 + ((index * 7) % 8) / 100
        db.session.add(EmailClassification(
            email_content=content, result=label, confidence=confidence,
            model_version=model_version,
        ))
        added["history"] += 1

    analyst = User.query.filter_by(username="demo.analyst").first()
    if analyst is None:
        analyst = User(username="demo.analyst", role="analyst", display_name="Tài khoản demo")
        analyst.set_password("DemoAnalyst123!")
        db.session.add(analyst)
        added["users"] = 1

    for address, reason in (("203.0.113.42", "IP ví dụ TEST-NET cho demo"),
                            ("198.51.100.27", "IP ví dụ TEST-NET cho demo")):
        if not BlockedIP.query.filter_by(address=address).first():
            db.session.add(BlockedIP(address=address, reason=reason))
            added["ipBlocklist"] += 1
    for domain, reason in (("claim-prize.test", "Domain giả lập phishing cho demo"),
                           ("secure-wallet.test", "Domain giả lập phishing cho demo")):
        if not BlockedDomain.query.filter_by(domain=domain).first():
            db.session.add(BlockedDomain(domain=domain, reason=reason))
            added["domainBlocklist"] += 1

    if not ModelInformation.query.filter_by(model_version="DEMO-SEED-NOT-TRAINED").first():
        # A placeholder provides a row in the model-history table without inventing metrics
        # or replacing the active model used by predictions.
        db.session.add(ModelInformation(
            model_name="Demo placeholder (chưa huấn luyện)",
            model_version="DEMO-SEED-NOT-TRAINED",
            is_active=False,
        ))
        added["modelInformation"] = 1

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    counts = {
        "dataset": dataset_result["total"],
        "history": EmailClassification.query.count(),
        "users": User.query.count(),
        "ipBlocklist": BlockedIP.query.count(),
        "domainBlocklist": BlockedDomain.query.count(),
        "modelInformation": ModelInformation.query.count(),
    }
    return jsonify({"message": "Đã nhập dữ liệu demo cho toàn bộ bảng; thao tác có thể chạy lại mà không nhân bản mẫu.",
                    "added": added, "counts": counts,
                    "demoAnalyst": {"username": "demo.analyst", "password": "DemoAnalyst123!"}}), 200
