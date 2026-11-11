from flask import Blueprint, request, jsonify
from backend.services.inspection_service import InspectionService
from backend.validation.exceptions import ValidationError

bp = Blueprint("inspection", __name__, url_prefix="/api")

@bp.route("/inspection-plans", methods=["GET"])
def get_inspection_plans():
    product_id = request.args.get("product_id")
    plans = InspectionService.get_inspection_plans(product_id=product_id)
    return jsonify(plans), 200

@bp.route("/inspection-plans", methods=["POST"])
def create_inspection_plan():
    data = request.get_json() or {}
    try:
        plan = InspectionService.create_inspection_plan(data)
        return jsonify(plan), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/inspections", methods=["GET"])
def get_inspections():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    result = request.args.get("result")
    order_id = request.args.get("order_id")
    res = InspectionService.get_inspection_results(page=page, per_page=per_page, search=search, result=result, order_id=order_id)
    return jsonify(res), 200

@bp.route("/inspections/<insp_id>", methods=["GET"])
def get_inspection(insp_id):
    try:
        insp = InspectionService.get_inspection_result(insp_id)
        return jsonify(insp), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/inspections", methods=["POST"])
def record_inspection():
    data = request.get_json() or {}
    try:
        insp = InspectionService.record_inspection_result(data)
        return jsonify(insp), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

