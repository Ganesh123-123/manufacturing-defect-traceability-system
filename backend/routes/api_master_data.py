from flask import Blueprint, request, jsonify
from backend.services.master_data_service import MasterDataService
from backend.validation.exceptions import ValidationError

bp = Blueprint("master_data", __name__, url_prefix="/api")

@bp.route("/products", methods=["GET"])
def get_products():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    category = request.args.get("category")
    res = MasterDataService.get_products(page=page, per_page=per_page, search=search, category=category)
    return jsonify(res), 200

@bp.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    try:
        p = MasterDataService.get_product(product_id)
        return jsonify(p), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    try:
        p = MasterDataService.create_product(data)
        return jsonify(p), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/suppliers", methods=["GET"])
def get_suppliers():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search")
    status = request.args.get("status")
    res = MasterDataService.get_suppliers(page=page, per_page=per_page, search=search, status=status)
    return jsonify(res), 200

@bp.route("/suppliers/<supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    try:
        s = MasterDataService.get_supplier(supplier_id)
        return jsonify(s), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 404

@bp.route("/suppliers", methods=["POST"])
def create_supplier():
    data = request.get_json() or {}
    try:
        s = MasterDataService.create_supplier(data)
        return jsonify(s), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/boms", methods=["GET"])
def get_boms():
    product_id = request.args.get("product_id")
    boms = MasterDataService.get_boms(parent_product_id=product_id)
    return jsonify(boms), 200

@bp.route("/boms", methods=["POST"])
def create_bom():
    data = request.get_json() or {}
    try:
        b = MasterDataService.create_bom(data)
        return jsonify(b), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/machines", methods=["GET"])
def get_machines():
    machines = MasterDataService.get_machines()
    return jsonify(machines), 200

@bp.route("/machines", methods=["POST"])
def create_machine():
    data = request.get_json() or {}
    try:
        m = MasterDataService.create_machine(data)
        return jsonify(m), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400

@bp.route("/process-steps", methods=["GET"])
def get_process_steps():
    steps = MasterDataService.get_process_steps()
    return jsonify(steps), 200

@bp.route("/process-steps", methods=["POST"])
def create_process_step():
    data = request.get_json() or {}
    try:
        s = MasterDataService.create_process_step(data)
        return jsonify(s), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "code": e.code}), 400
