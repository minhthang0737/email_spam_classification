"""Seed training dataset with sample emails."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models.email_dataset import EmailDataset

SAMPLE_DATA = [
    ("Congratulations! You won $5000. Click here to claim.", "SPAM"),
    ("You have won a free prize. Claim your reward now.", "SPAM"),
    ("Free money waiting for you. Act now!", "SPAM"),
    ("Winner! Your lottery prize is ready.", "SPAM"),
    ("Limited offer: earn cash instantly.", "SPAM"),
    ("Meeting at 10 AM tomorrow in room 201.", "NOT_SPAM"),
    ("Please review the project document before Friday.", "NOT_SPAM"),
    ("Can we schedule a meeting tomorrow afternoon?", "NOT_SPAM"),
    ("The team lunch is at 12 PM today.", "NOT_SPAM"),
    ("Reminder: submit your assignment by Sunday.", "NOT_SPAM"),
    ("Your account statement is available online.", "NOT_SPAM"),
    ("Project update: sprint review on Thursday.", "NOT_SPAM"),
]

app = create_app()

with app.app_context():
    existing = EmailDataset.query.count()
    if existing > 0:
        print(f"Dataset already has {existing} records. Skipping seed.")
    else:
        for email_content, label in SAMPLE_DATA:
            db.session.add(EmailDataset(email_content=email_content, label=label))
        db.session.commit()
        print(f"Seeded {len(SAMPLE_DATA)} dataset records.")
