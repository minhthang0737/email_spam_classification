import ipaddress
import re

from flask import Blueprint, jsonify, request

from app import db
from app.auth import login_required
from app.models.ip_reputation import BlockedIP, BlockedDomain
from app.utils.errors import not_found_error, validation_error

ip_bp = Blueprint("ip_reputation", __name__, url_prefix="/api/ip")
IP_PATTERN = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])|(?<![\w:])[0-9a-fA-F:]{3,39}(?![\w:])")
DOMAIN_SOURCE_PATTERN = re.compile(
    r"(?i)(?:[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@|(?:https?://|www\.))"
    r"([a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,63})"
)
DOMAIN_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_domain(value):
    domain = str(value or "").strip().rstrip(".").lower()
    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        raise ValueError("Tên miền không hợp lệ.")
    labels = domain.split(".")
    if len(domain) > 253 or len(labels) < 2 or any(
        not DOMAIN_LABEL_PATTERN.fullmatch(label) for label in labels
    ):
        raise ValueError("Tên miền không hợp lệ.")
    return domain


def inspect_address(value):
    try:
        address = ipaddress.ip_address(value.strip("[](),;"))
    except ValueError:
        return None
    blocked = BlockedIP.query.filter_by(address=str(address)).first()
    return {"ip": str(address), "version": address.version,
            "scope": "public" if address.is_global else "private/reserved",
            "isPublic": address.is_global, "blocked": blocked is not None,
            "reason": blocked.reason if blocked else None}


@ip_bp.post("/check")
@login_required()
def check_ip():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", data.get("ip", "")))[:20000]
    values = []
    for candidate in IP_PATTERN.findall(text):
        result = inspect_address(candidate)
        if result and result["ip"] not in {item["ip"] for item in values}:
            values.append(result)
    direct = inspect_address(text.strip())
    if direct and direct["ip"] not in {item["ip"] for item in values}:
        values.append(direct)
    domains = []
    for candidate in DOMAIN_SOURCE_PATTERN.findall(text):
        try:
            domain = normalize_domain(candidate)
        except ValueError:
            continue
        if domain in {item["domain"] for item in domains}:
            continue
        blocked = BlockedDomain.query.filter_by(domain=domain).first()
        domains.append({"domain": domain, "blocked": blocked is not None,
                        "reason": blocked.reason if blocked else None})
    return jsonify({"data": values, "domains": domains,
                    "count": len(values), "domainCount": len(domains)}), 200


@ip_bp.get("/blocklist")
@login_required("admin")
def list_blocked_ips():
    rows = BlockedIP.query.order_by(BlockedIP.id.desc()).all()
    return jsonify({"data": [row.to_dict() for row in rows]}), 200


@ip_bp.post("/blocklist")
@login_required("admin")
def add_blocked_ip():
    data = request.get_json(silent=True) or {}
    try:
        address = str(ipaddress.ip_address(str(data.get("ip", "")).strip()))
    except ValueError:
        return validation_error("Địa chỉ IP không hợp lệ.")
    if BlockedIP.query.filter_by(address=address).first():
        return jsonify({"message": "IP đã có trong danh sách chặn."}), 409
    reason = str(data.get("reason", "Được quản trị viên đánh dấu")).strip()[:300]
    row = BlockedIP(address=address, reason=reason or "Được quản trị viên đánh dấu")
    db.session.add(row)
    db.session.commit()
    return jsonify(row.to_dict()), 201


@ip_bp.put("/blocklist/<int:row_id>")
@login_required("admin")
def update_blocked_ip(row_id):
    row = db.session.get(BlockedIP, row_id)
    if row is None:
        return not_found_error("Không tìm thấy IP.")
    data = request.get_json(silent=True) or {}
    if "ip" in data:
        try:
            address = str(ipaddress.ip_address(str(data["ip"]).strip()))
        except ValueError:
            return validation_error("Địa chỉ IP không hợp lệ.")
        duplicate = BlockedIP.query.filter(BlockedIP.address == address, BlockedIP.id != row_id).first()
        if duplicate:
            return jsonify({"message": "IP đã có trong danh sách chặn."}), 409
        row.address = address
    if "reason" in data:
        row.reason = str(data["reason"]).strip()[:300] or "Được quản trị viên đánh dấu"
    db.session.commit()
    return jsonify(row.to_dict()), 200


@ip_bp.delete("/blocklist/<int:row_id>")
@login_required("admin")
def delete_blocked_ip(row_id):
    row = db.session.get(BlockedIP, row_id)
    if row is None:
        return not_found_error("Không tìm thấy IP.")
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "Đã xóa IP khỏi danh sách chặn."}), 200


@ip_bp.get("/domain-blocklist")
@login_required("admin")
def list_blocked_domains():
    rows = BlockedDomain.query.order_by(BlockedDomain.id.desc()).all()
    return jsonify({"data": [row.to_dict() for row in rows]}), 200


@ip_bp.post("/domain-blocklist")
@login_required("admin")
def add_blocked_domain():
    data = request.get_json(silent=True) or {}
    try:
        domain = normalize_domain(data.get("domain"))
    except ValueError as error:
        return validation_error(str(error))
    if BlockedDomain.query.filter_by(domain=domain).first():
        return jsonify({"message": "Domain đã có trong danh sách chặn."}), 409
    reason = str(data.get("reason", "Được quản trị viên đánh dấu")).strip()[:300]
    row = BlockedDomain(domain=domain, reason=reason or "Được quản trị viên đánh dấu")
    db.session.add(row)
    db.session.commit()
    return jsonify(row.to_dict()), 201


@ip_bp.put("/domain-blocklist/<int:row_id>")
@login_required("admin")
def update_blocked_domain(row_id):
    row = db.session.get(BlockedDomain, row_id)
    if row is None:
        return not_found_error("Không tìm thấy domain.")
    data = request.get_json(silent=True) or {}
    if "domain" in data:
        try:
            domain = normalize_domain(data["domain"])
        except ValueError as error:
            return validation_error(str(error))
        duplicate = BlockedDomain.query.filter(
            BlockedDomain.domain == domain, BlockedDomain.id != row_id
        ).first()
        if duplicate:
            return jsonify({"message": "Domain đã có trong danh sách chặn."}), 409
        row.domain = domain
    if "reason" in data:
        row.reason = str(data["reason"]).strip()[:300] or "Được quản trị viên đánh dấu"
    db.session.commit()
    return jsonify(row.to_dict()), 200


@ip_bp.delete("/domain-blocklist/<int:row_id>")
@login_required("admin")
def delete_blocked_domain(row_id):
    row = db.session.get(BlockedDomain, row_id)
    if row is None:
        return not_found_error("Không tìm thấy domain.")
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "Đã xóa domain khỏi danh sách chặn."}), 200
