from flask import Blueprint, request, jsonify
from backend.services.production_service import ProductionService
from backend.validation.exceptions import ValidationError, MaterialReconciliationException

bp = Blueprint("production", __name__, url_prefix="/api")

@bp.route("/material-lots", methods=["GET"])
def get_material_lots():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    status = request.args.get("status")
    supplier_id = request.args.get("supplier_id")
    res = ProductionService.get_material_lots(page=page, per_page=per_page, search=search, status=status, supplier_id=supplier_id)
    return jsonify(res), 200

@bp.route("/material-lots/<lot_id>", methods=["GET"])
def get_material_lot(lot_id):
    try:
        lot = ProductionService.get_material_lot(lot_id)
        return jsonify(lot), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/material-lots", methods=["POST"])
def create_material_lot():
    data = request.get_json() or {}
    try:
        lot = ProductionService.create_material_lot(data)
        return jsonify(lot), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/production-orders", methods=["GET"])
def get_production_orders():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    status = request.args.get("status")
    product_id = request.args.get("product_id")
    res = ProductionService.get_production_orders(page=page, per_page=per_page, search=search, status=status, product_id=product_id)
    return jsonify(res), 200

@bp.route("/production-orders/<order_id>", methods=["GET"])
def get_production_order(order_id):
    try:
        order = ProductionService.get_production_order(order_id)
        return jsonify(order), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/production-orders", methods=["POST"])
def create_production_order():
    data = request.get_json() or {}
    try:
        order = ProductionService.create_production_order(data)
        return jsonify(order), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/material-consumptions", methods=["POST"])
def record_material_consumption():
    data = request.get_json() or {}
    try:
        cons = ProductionService.record_material_consumption(data)
        return jsonify(cons), 201
    except (ValidationError, MaterialReconciliationException) as e:
        return jsonify({"error": e.message, "code": getattr(e, "code", "VALIDATION_ERROR")}), 400

