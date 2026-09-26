from flask import Blueprint, g, jsonify, request

from app import db
from app.auth import login_required
from app.models.user import User
from app.utils.errors import not_found_error, validation_error

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("")
@login_required("admin")
def list_users():
    return jsonify({"data": [u.to_dict() for u in User.query.order_by(User.id).all()]}), 200


@users_bp.post("")
@login_required("admin")
def create_user():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    role = str(data.get("role", "analyst")).strip().lower()
    if len(username) < 3 or len(username) > 80:
        return validation_error("Tên đăng nhập phải có từ 3 đến 80 ký tự.")
    if len(password) < 8:
        return validation_error("Mật khẩu phải có ít nhất 8 ký tự.")
    if role not in ("admin", "analyst"):
        return validation_error("Role phải là admin hoặc analyst.")
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Tên đăng nhập đã tồn tại."}), 409
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@users_bp.put("/<int:user_id>")
@login_required("admin")
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return not_found_error("Không tìm thấy tài khoản.")
    data = request.get_json(silent=True) or {}
    role = str(data.get("role", user.role)).strip().lower()
    active = data.get("isActive", user.is_active)
    if role not in ("admin", "analyst") or not isinstance(active, bool):
        return validation_error("Role hoặc trạng thái tài khoản không hợp lệ.")
    if user.role == "admin" and user.is_active and (role != "admin" or not active):
        remaining = User.query.filter_by(role="admin", is_active=True).filter(User.id != user.id).count()
        if remaining == 0:
            return jsonify({"message": "Không thể vô hiệu hóa hoặc hạ quyền quản trị viên cuối cùng."}), 409
    user.role = role
    user.is_active = active
    password = data.get("password")
    if password:
        if len(str(password)) < 8:
            return validation_error("Mật khẩu phải có ít nhất 8 ký tự.")
        user.set_password(str(password))
    db.session.commit()
    return jsonify(user.to_dict()), 200


@users_bp.delete("/<int:user_id>")
@login_required("admin")
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return not_found_error("Không tìm thấy tài khoản.")
    if user.id == g.user.id:
        return jsonify({"message": "Không thể xóa tài khoản đang đăng nhập."}), 409
    if user.role == "admin" and user.is_active and User.query.filter_by(role="admin", is_active=True).filter(User.id != user.id).count() == 0:
        return jsonify({"message": "Không thể xóa quản trị viên cuối cùng."}), 409
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Đã xóa tài khoản."}), 200
