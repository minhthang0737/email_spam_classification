import re

from flask import Blueprint, g, jsonify, request

from app import db
from app.auth import login_required
from app.utils.errors import validation_error


account_bp = Blueprint("account", __name__, url_prefix="/api/account")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@account_bp.put("/profile")
@login_required()
def update_profile():
    data = request.get_json(silent=True) or {}
    display_name = str(data.get("displayName", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    if len(display_name) > 120:
        return validation_error("Tên hiển thị tối đa 120 ký tự.")
    if len(email) > 254 or (email and not EMAIL_PATTERN.fullmatch(email)):
        return validation_error("Email không hợp lệ.")
    g.user.display_name = display_name or None
    g.user.email = email or None
    db.session.commit()
    return jsonify({"message": "Đã cập nhật hồ sơ.", "user": g.user.to_dict()}), 200


@account_bp.put("/password")
@login_required()
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = str(data.get("currentPassword", ""))
    new_password = str(data.get("newPassword", ""))
    if not g.user.check_password(current_password):
        return jsonify({"message": "Mật khẩu hiện tại không đúng."}), 400
    if len(new_password) < 8:
        return validation_error("Mật khẩu mới phải có ít nhất 8 ký tự.")
    if new_password == current_password:
        return validation_error("Mật khẩu mới phải khác mật khẩu hiện tại.")
    g.user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Đã đổi mật khẩu thành công."}), 200
