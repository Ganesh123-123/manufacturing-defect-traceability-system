from flask import Blueprint, request, jsonify
from backend.services.capa_service import CAPAService
from backend.validation.exceptions import ValidationError, LifecycleViolationException

bp = Blueprint("capa", __name__, url_prefix="/api")

@bp.route("/capas", methods=["GET"])
def get_capas():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    status = request.args.get("status")
    res = CAPAService.get_capas(page=page, per_page=per_page, search=search, status=status)
    return jsonify(res), 200

@bp.route("/capas/<capa_id>", methods=["GET"])
def get_capa(capa_id):
    try:
        capa = CAPAService.get_capa(capa_id)
        return jsonify(capa), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/capas", methods=["POST"])
def create_capa():
    data = request.get_json() or {}
    try:
        capa = CAPAService.create_capa(data)
        return jsonify(capa), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/capas/<capa_id>/verify", methods=["POST"])
def verify_capa(capa_id):
    data = request.get_json() or {}
    try:
        capa = CAPAService.verify_capa(capa_id, data)
        return jsonify(capa), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/capas/<capa_id>/close", methods=["POST"])
def close_capa(capa_id):
    data = request.get_json() or {}
    try:
        capa = CAPAService.close_capa(capa_id, data)
        return jsonify(capa), 200
    except LifecycleViolationException as e:
        return jsonify({
            "error": e.message,
            "code": e.code,
            "status": "REJECTED_LIFECYCLE_VIOLATION"
        }), 400
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400
