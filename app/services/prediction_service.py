from app import db
from app.models.email_classification import EmailClassification
from app.ml.predictor import ActiveModelNotFoundError, predict_email


def classify_and_save(email_content: str):
    try:
        prediction = predict_email(email_content)
    except ActiveModelNotFoundError as exc:
        raise exc

    classification = EmailClassification(
        email_content=email_content.strip(),
        result=prediction["result"],
        confidence=prediction["confidence"],
        model_version=prediction["model_version"],
    )

    db.session.add(classification)
    db.session.commit()

    return classification
