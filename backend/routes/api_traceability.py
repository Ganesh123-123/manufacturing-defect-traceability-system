from flask import Blueprint, request, jsonify
from backend.services.traceability_service import TraceabilityService
from backend.validation.exceptions import ValidationError

bp = Blueprint("traceability", __name__, url_prefix="/api")

@bp.route("/traceability", methods=["GET"])
def trace_entity():
    q_type = request.args.get("type", "defect")
    q_id = request.args.get("id")
    if not q_id:
        return jsonify({"error": "Query parameter 'id' is required.", "code": "MISSING_PARAM"}), 400
    
    try:
        chain = TraceabilityService.trace(q_type, q_id)
        return jsonify(chain), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code, "status": "BROKEN_OR_NOT_FOUND"}), 404

@bp.route("/traceability/defect/<defect_id>", methods=["GET"])
def trace_defect(defect_id):
    try:
        chain = TraceabilityService.trace_defect(defect_id)
        return jsonify(chain), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code, "status": "BROKEN_OR_NOT_FOUND"}), 404

