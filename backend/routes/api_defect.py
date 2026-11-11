from flask import Blueprint, request, jsonify
from backend.services.defect_service import DefectService
from backend.validation.exceptions import ValidationError

bp = Blueprint("defect", __name__, url_prefix="/api")

@bp.route("/defects", methods=["GET"])
def get_defects():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    severity = request.args.get("severity")
    status = request.args.get("status")
    disposition = request.args.get("disposition")
    res = DefectService.get_defects(
        page=page, per_page=per_page, search=search, severity=severity, status=status, disposition=disposition
    )
    return jsonify(res), 200

@bp.route("/defects/<defect_id>", methods=["GET"])
def get_defect(defect_id):
    try:
        defect = DefectService.get_defect(defect_id)
        return jsonify(defect), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/defects", methods=["POST"])
def record_defect():
    data = request.get_json() or {}
    try:
        defect = DefectService.record_defect(data)
        return jsonify(defect), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/defects/<defect_id>/containment", methods=["POST"])
def create_containment(defect_id):
    data = request.get_json() or {}
    try:
        ca = DefectService.create_containment_action(defect_id, data)
        return jsonify(ca), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400
