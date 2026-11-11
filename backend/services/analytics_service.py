from sqlalchemy import func
from datetime import datetime
from backend.database.connection import db
from backend.models import (
    Product, Supplier, MaterialLot, ProductionOrder, InspectionResult,
    Defect, CorrectiveAction, Machine
)

class AnalyticsService:
    @staticmethod
    def get_dashboard_kpis():
        total_products = db.session.query(func.count(Product.id)).scalar() or 0
        total_suppliers = db.session.query(func.count(Supplier.id)).scalar() or 0
        total_material_lots = db.session.query(func.count(MaterialLot.id)).scalar() or 0
        total_production_orders = db.session.query(func.count(ProductionOrder.id)).scalar() or 0
        total_inspections = db.session.query(func.count(InspectionResult.id)).scalar() or 0
        total_defects = db.session.query(func.count(Defect.id)).scalar() or 0

        # Calculate total inspected units & defective units for Defect Rate
        inspected_units = db.session.query(func.sum(InspectionResult.inspected_quantity)).scalar() or 0
        defective_units = db.session.query(func.sum(Defect.defect_quantity)).scalar() or 0

        defect_rate = (float(defective_units) / float(inspected_units) * 100.0) if inspected_units > 0 else 0.0

        # Rework & Scrap quantities from source records (Rule 10)
        rework_quantity = db.session.query(func.sum(Defect.rework_quantity)).scalar() or 0
        scrap_quantity = db.session.query(func.sum(Defect.scrap_quantity)).scalar() or 0

        # Open corrective actions
        open_capas = db.session.query(func.count(CorrectiveAction.id)).filter(
            CorrectiveAction.status.in_(["OPEN", "IN_PROGRESS", "CONTAINMENT", "PENDING_VERIFICATION"])
        ).scalar() or 0

        return {
            "total_products": total_products,
            "total_suppliers": total_suppliers,
            "total_material_lots": total_material_lots,
            "total_production_orders": total_production_orders,
            "total_inspections": total_inspections,
            "total_defects": total_defects,
            "total_inspected_units": int(inspected_units),
            "total_defective_units": int(defective_units),
            "defect_rate": round(defect_rate, 2),
            "rework_quantity": int(rework_quantity),
            "scrap_quantity": int(scrap_quantity),
            "open_corrective_actions": open_capas
        }

    @staticmethod
    def get_supplier_defect_analysis(limit=10):
        # Defect count and rate per supplier
        results = db.session.query(
            Supplier.name,
            func.count(Defect.id).label("defect_count"),
            func.coalesce(func.sum(Defect.defect_quantity), 0).label("defective_units")
        ).join(MaterialLot, MaterialLot.supplier_id == Supplier.id)\
         .join(Defect, Defect.material_lot_id == MaterialLot.id)\
         .group_by(Supplier.name)\
         .order_by(func.count(Defect.id).desc())\
         .limit(limit).all()

        return [
            {
                "supplier_name": r[0],
                "defect_count": r[1],
                "defective_units": int(r[2])
            }
            for r in results
        ]

    @staticmethod
    def get_machine_defect_analysis(limit=10):
        results = db.session.query(
            Machine.name,
            Machine.line,
            func.count(Defect.id).label("defect_count"),
            func.coalesce(func.sum(Defect.scrap_quantity), 0).label("scrap_quantity"),
            func.coalesce(func.sum(Defect.rework_quantity), 0).label("rework_quantity")
        ).join(Defect, Defect.machine_id == Machine.id)\
         .group_by(Machine.name, Machine.line)\
         .order_by(func.count(Defect.id).desc())\
         .limit(limit).all()

        return [
            {
                "machine_name": f"{r[0]} ({r[1]})",
                "defect_count": r[2],
                "scrap_quantity": int(r[3]),
                "rework_quantity": int(r[4])
            }
            for r in results
        ]

    @staticmethod
    def get_product_defect_rates(limit=10):
        results = db.session.query(
            Product.id,
            Product.name,
            func.coalesce(func.sum(InspectionResult.inspected_quantity), 0).label("inspected"),
            func.coalesce(func.sum(InspectionResult.failed_quantity), 0).label("failed")
        ).join(ProductionOrder, ProductionOrder.product_id == Product.id)\
         .join(InspectionResult, InspectionResult.production_order_id == ProductionOrder.id)\
         .group_by(Product.id, Product.name)\
         .order_by(func.coalesce(func.sum(InspectionResult.failed_quantity), 0).desc())\
         .limit(limit).all()

        items = []
        for r in results:
            insp = float(r[2])
            failed = float(r[3])
            rate = (failed / insp * 100.0) if insp > 0 else 0.0
            items.append({
                "product_sku": r[0],
                "product_name": r[1],
                "inspected_quantity": int(insp),
                "failed_quantity": int(failed),
                "defect_rate": round(rate, 2)
            })
        return items

    @staticmethod
    def get_monthly_defect_trends():
        # Aggregated trends
        if db.engine.name == "sqlite":
            period_expr = func.strftime("%Y-%m", Defect.detected_at)
        elif db.engine.name == "postgresql":
            period_expr = func.to_char(Defect.detected_at, "YYYY-MM")
        else:
            period_expr = func.date_format(Defect.detected_at, "%Y-%m")
        results = db.session.query(
            period_expr.label("month"),
            func.count(Defect.id),
            func.coalesce(func.sum(Defect.rework_quantity), 0),
            func.coalesce(func.sum(Defect.scrap_quantity), 0)
        ).group_by(period_expr)\
         .order_by(period_expr.asc())\
         .all()

        return [
            {
                "month": r[0] or "2026-01",
                "defect_count": r[1],
                "rework_quantity": int(r[2]),
                "scrap_quantity": int(r[3])
            }
            for r in results
        ]

    @staticmethod
    def get_rework_vs_scrap():
        rework = db.session.query(func.coalesce(func.sum(Defect.rework_quantity), 0)).scalar() or 0
        scrap = db.session.query(func.coalesce(func.sum(Defect.scrap_quantity), 0)).scalar() or 0
        rework_int = int(rework)
        scrap_int = int(scrap)
        total = rework_int + scrap_int
        return {
            "rework": rework_int,
            "scrap": scrap_int,
            "total": total,
            "rework_percentage": round((float(rework_int) / float(total) * 100.0), 1) if total > 0 else 0.0,
            "scrap_percentage": round((float(scrap_int) / float(total) * 100.0), 1) if total > 0 else 0.0
        }

    @staticmethod
    def get_inspection_pass_fail():
        passed = db.session.query(func.coalesce(func.sum(InspectionResult.passed_quantity), 0)).scalar() or 0
        failed = db.session.query(func.coalesce(func.sum(InspectionResult.failed_quantity), 0)).scalar() or 0
        passed_int = int(passed)
        failed_int = int(failed)
        total = passed_int + failed_int
        return {
            "passed_quantity": passed_int,
            "failed_quantity": failed_int,
            "total_inspected": total,
            "pass_rate": round((float(passed_int) / float(total) * 100.0), 1) if total > 0 else 0.0,
            "fail_rate": round((float(failed_int) / float(total) * 100.0), 1) if total > 0 else 0.0
        }

    @staticmethod
    def get_capa_status_distribution():
        results = db.session.query(
            CorrectiveAction.status,
            func.count(CorrectiveAction.id)
        ).group_by(CorrectiveAction.status).all()

        statuses = {
            "OPEN": 0,
            "IN_PROGRESS": 0,
            "CONTAINMENT": 0,
            "PENDING_VERIFICATION": 0,
            "VERIFIED": 0,
            "CLOSED": 0
        }
        for status, count in results:
            if status in statuses:
                statuses[status] = count
            else:
                statuses[status] = count
        return statuses
