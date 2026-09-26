from functools import wraps

from flask import g, jsonify, redirect, request, session, url_for

from app import db
from app.models.user import User


def load_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None
    if g.user and not g.user.is_active:
        session.clear()
        g.user = None


def login_required(role=None):
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = getattr(g, "user", None)
            if not user:
                if request.path.startswith("/api/"):
                    return jsonify({"message": "Đăng nhập để tiếp tục.", "code": "AUTH_REQUIRED"}), 401
                return redirect(url_for("views.login", next=request.full_path.rstrip("?")))
            if role and user.role != role:
                if request.path.startswith("/api/"):
                    return jsonify({"message": "Bạn không có quyền thực hiện thao tác này.", "code": "FORBIDDEN"}), 403
                return redirect(url_for("views.index"))
            return view(*args, **kwargs)
        return wrapped
    return decorate
