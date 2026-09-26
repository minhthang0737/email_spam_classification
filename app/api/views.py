from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth import login_required
from app.models.user import User

views_bp = Blueprint("views", __name__)


@views_bp.get("/")
def index():
    return render_template("classify.html")


@views_bp.get("/history")
@login_required()
def history():
    return render_template("history.html")


@views_bp.get("/admin/dataset")
@login_required("admin")
def admin_dataset():
    return render_template("admin_dataset.html")


@views_bp.get("/admin/model")
@login_required("admin")
def admin_model():
    return render_template("admin_model.html")


@views_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if user and user.is_active and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            destination = request.form.get("next", "")
            if destination.startswith("/") and not destination.startswith("//") and "\\" not in destination:
                return redirect(destination)
            return redirect(url_for("views.index"))
        flash("Sai tên đăng nhập hoặc mật khẩu.", "danger")
    return render_template("login.html")


@views_bp.post("/logout")
@login_required()
def logout():
    session.clear()
    return redirect(url_for("views.login"))


@views_bp.get("/admin/ip")
@login_required("admin")
def admin_ip():
    return render_template("admin_ip.html")


@views_bp.get("/admin/users")
@login_required("admin")
def admin_users():
    return render_template("admin_users.html")


@views_bp.get("/settings")
@login_required()
def settings():
    return render_template("settings.html")
