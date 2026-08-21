from flask import jsonify


def error_response(message, code, status):
    return jsonify({"message": message, "code": code}), status


def validation_error(message):
    return error_response(message, "VALIDATION_ERROR", 400)


def not_found_error(message):
    return error_response(message, "NOT_FOUND", 404)


def conflict_error(message):
    return error_response(message, "CONFLICT", 409)


def server_error(message="Internal server error."):
    return error_response(message, "INTERNAL_ERROR", 500)
