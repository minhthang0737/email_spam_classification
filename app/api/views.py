from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)


@views_bp.get("/")
def index():
    return render_template("classify.html")


@views_bp.get("/history")
def history():
    return render_template("history.html")


@views_bp.get("/admin/dataset")
def admin_dataset():
    return render_template("admin_dataset.html")


@views_bp.get("/admin/model")
def admin_model():
    return render_template("admin_model.html")
