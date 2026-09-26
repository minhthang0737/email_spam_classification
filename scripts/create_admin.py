"""Create the initial administrator account from environment settings."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models.user import User

app = create_app()
username = os.getenv("ADMIN_USERNAME", "admin").strip()
password = os.getenv("ADMIN_PASSWORD", "Admin123!")

if len(password) < 8:
    raise SystemExit("ADMIN_PASSWORD must contain at least 8 characters.")

with app.app_context():
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"Administrator '{username}' already exists; password unchanged.")
    else:
        user = User(username=username, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created administrator '{username}'. Set ADMIN_PASSWORD before first run outside the demo.")
