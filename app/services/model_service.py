from datetime import datetime

from app import db
from app.models.model_information import ModelInformation


def save_model_information(
    model_name,
    model_version,
    accuracy,
    precision_score,
    recall_score,
    f1_score
):
    """
    Lưu thông tin model sau khi training.
    Model mới sẽ được active.
    Model cũ sẽ inactive.
    """

    # Deactivate tất cả model hiện tại
    ModelInformation.query.update(
        {
            ModelInformation.is_active: False
        }
    )

    # Tạo model information mới
    model_info = ModelInformation(
        model_name=model_name,
        model_version=model_version,
        accuracy=accuracy,
        precision_score=precision_score,
        recall_score=recall_score,
        f1_score=f1_score,
        trained_at=datetime.utcnow(),
        is_active=True
    )

    db.session.add(model_info)
    db.session.commit()

    return model_info