"""Initialize database tables."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created.")
