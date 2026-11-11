import os
import json
from flask import Blueprint, jsonify, send_from_directory, current_app
from backend.database.connection import db
from backend.validation.rules import run_full_database_validation

bp = Blueprint("system", __name__, url_prefix="/api/system")

@bp.route("/health", methods=["GET"])
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "engine": db.engine.name
    }), 200

@bp.route("/validate", methods=["GET", "POST"])
@bp.route("/audit-summary", methods=["GET"])
@bp.route("/validation-report", methods=["GET"])
def validate_system():
    summary = run_full_database_validation(db.session)
    if not current_app.config.get("TESTING"):
        export_dir = current_app.config.get("EXPORT_DIR", "backend/exports")
        os.makedirs(export_dir, exist_ok=True)
        summary_path = os.path.join(export_dir, "validation_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
    return jsonify(summary), 200

@bp.route("/anomaly-scenarios", methods=["GET"])
def anomaly_scenarios():
    scenarios = [
        {
            "scenario_id": "SCENARIO_1",
            "name": "Defect links to nonexistent material lot",
            "expected_behavior": "Detect broken foreign key or traceability reference",
            "validation_rule": "Defect.material_lot_id must match an existing MaterialLot.id"
        },
        {
            "scenario_id": "SCENARIO_2",
            "name": "BOM material is not consumed",
            "expected_behavior": "Generate material consumption exception",
            "validation_rule": "Completed orders must consume all required active BOM component SKUs"
        },
        {
            "scenario_id": "SCENARIO_3",
            "name": "Corrective action closes before verification",
            "expected_behavior": "Reject closure and record lifecycle violation event",
            "validation_rule": "CAPA cannot transition to CLOSED unless verified_date and verified_by are recorded"
        },
        {
            "scenario_id": "SCENARIO_4",
            "name": "Defect count exceeds inspected quantity",
            "expected_behavior": "Reject invalid inspection / defect quantity",
            "validation_rule": "Defect quantity must be <= inspected quantity and inspection passed+failed == inspected"
        },
        {
            "scenario_id": "SCENARIO_5",
            "name": "Traceability chain breaks",
            "expected_behavior": "Identify missing upstream or downstream relationship",
            "validation_rule": "All defects must trace forward/backward through production orders and product SKUs"
        }
    ]
    return jsonify(scenarios), 200

@bp.route("/ground-truth", methods=["GET"])
def get_ground_truth():
    export_dir = current_app.config.get("EXPORT_DIR", "backend/exports")
    gt_json = os.path.join(export_dir, "ground_truth.json")
    if os.path.exists(gt_json):
        with open(gt_json, "r") as f:
            return jsonify(json.load(f)), 200
    return jsonify([]), 200

@bp.route("/reproducibility", methods=["GET"])
@bp.route("/reproducibility-report", methods=["GET"])
def get_reproducibility():
    export_dir = current_app.config.get("EXPORT_DIR", "backend/exports")
    rep_file = os.path.join(export_dir, "reproducibility_report.json")
    if os.path.exists(rep_file):
        with open(rep_file, "r") as f:
            return jsonify(json.load(f)), 200
    return jsonify({"status": "not_generated"}), 404

@bp.route("/exports/<path:filename>", methods=["GET"])
def download_export(filename):
    export_dir = current_app.config.get("EXPORT_DIR", "backend/exports")
    return send_from_directory(export_dir, filename, as_attachment=True)

