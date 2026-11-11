from flask import Blueprint, jsonify
from backend.services.analytics_service import AnalyticsService

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@bp.route("/dashboard", methods=["GET"])
@bp.route("/kpi-summary", methods=["GET"])
def get_dashboard():
    kpis = AnalyticsService.get_dashboard_kpis()
    return jsonify(kpis), 200

@bp.route("/suppliers", methods=["GET"])
@bp.route("/top-defective-suppliers", methods=["GET"])
def get_supplier_analysis():
    data = AnalyticsService.get_supplier_defect_analysis()
    return jsonify(data), 200

@bp.route("/machines", methods=["GET"])
@bp.route("/machine-defect-scrap", methods=["GET"])
@bp.route("/machine-defects", methods=["GET"])
def get_machine_analysis():
    data = AnalyticsService.get_machine_defect_analysis()
    return jsonify(data), 200

@bp.route("/products", methods=["GET"])
@bp.route("/product-defect-rates", methods=["GET"])
@bp.route("/highest-defect-products", methods=["GET"])
def get_product_analysis():
    data = AnalyticsService.get_product_defect_rates()
    return jsonify(data), 200

@bp.route("/monthly-trends", methods=["GET"])
def get_monthly_trends():
    data = AnalyticsService.get_monthly_defect_trends()
    return jsonify(data), 200

@bp.route("/rework-vs-scrap", methods=["GET"])
def get_rework_vs_scrap():
    data = AnalyticsService.get_rework_vs_scrap()
    return jsonify(data), 200

@bp.route("/pass-fail", methods=["GET"])
def get_pass_fail():
    data = AnalyticsService.get_inspection_pass_fail()
    return jsonify(data), 200

@bp.route("/capa-distribution", methods=["GET"])
@bp.route("/capa-status", methods=["GET"])
def get_capa_distribution():
    data = AnalyticsService.get_capa_status_distribution()
    return jsonify(data), 200

