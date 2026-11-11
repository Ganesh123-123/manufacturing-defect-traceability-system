from datetime import datetime
from backend.database.connection import db, get_session
from backend.models import (
    InspectionPlan, InspectionResult, ProductionOrder, ProcessStep, Machine
)
from backend.validation.exceptions import ValidationError
from backend.validation.rules import validate_inspection_quantities

class InspectionService:
    @staticmethod
    def get_inspection_plans(product_id=None):
        query = InspectionPlan.query
        if product_id:
            query = query.filter_by(product_id=product_id)
        return [ip.to_dict() for ip in query.all()]

    @staticmethod
    def create_inspection_plan(data):
        if not data.get("id") or not data.get("product_id") or not data.get("name"):
            raise ValidationError("id, product_id, and name are required.")
        with get_session() as session:
            ip = InspectionPlan(
                id=data["id"],
                product_id=data["product_id"],
                step_id=data.get("step_id"),
                name=data["name"],
                sampling_type=data.get("sampling_type", "SAMPLE"),
                sample_size_percentage=float(data.get("sample_size_percentage", 10.0)),
                criteria=data.get("criteria", "Standard Visual and Dimensional Check"),
                is_active=bool(data.get("is_active", True))
            )
            session.add(ip)
            return ip.to_dict()

    @staticmethod
    def get_inspection_results(page=1, per_page=50, search=None, result=None, order_id=None):
        query = InspectionResult.query
        if search:
            query = query.filter(
                InspectionResult.id.ilike(f"%{search}%") |
                InspectionResult.production_order_id.ilike(f"%{search}%") |
                InspectionResult.inspector_name.ilike(f"%{search}%")
            )
        if result:
            query = query.filter(InspectionResult.result == result)
        if order_id:
            query = query.filter(InspectionResult.production_order_id == order_id)
        
        total = query.count()
        insps = query.order_by(InspectionResult.inspected_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [i.to_dict() for i in insps],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_inspection_result(insp_id):
        insp = InspectionResult.query.get(insp_id)
        if not insp:
            raise ValidationError(f"Inspection Result {insp_id} not found", code="NOT_FOUND")
        res = insp.to_dict()
        res["defects"] = [d.to_dict() for d in insp.defects]
        return res

    @staticmethod
    def record_inspection_result(data):
        # Rule 5: Inspection results must reference valid inspection plans
        plan_id = data.get("inspection_plan_id")
        plan = InspectionPlan.query.get(plan_id)
        if not plan_id or not plan:
            raise ValidationError(f"Valid inspection_plan_id required. Plan {plan_id} not found.")

        order_id = data.get("production_order_id")
        order = ProductionOrder.query.get(order_id)
        if not order_id or not order:
            raise ValidationError(f"Valid production_order_id required. Order {order_id} not found.")

        insp_id = data.get("id")
        if not insp_id:
            raise ValidationError("Inspection id is required.")
        if InspectionResult.query.get(insp_id):
            raise ValidationError(f"Inspection {insp_id} already exists.", code="DUPLICATE_KEY")

        inspected_qty = int(data.get("inspected_quantity", 0))
        passed_qty = int(data.get("passed_quantity", 0))
        failed_qty = int(data.get("failed_quantity", 0))

        # Rule 7 & 11: Validate inspection quantities
        validate_inspection_quantities(inspected_qty, passed_qty, failed_qty)

        res_status = "PASS" if failed_qty == 0 else "FAIL"

        with get_session() as session:
            insp = InspectionResult(
                id=insp_id,
                inspection_plan_id=plan_id,
                production_order_id=order_id,
                step_id=data.get("step_id") or plan.step_id,
                machine_id=data.get("machine_id"),
                inspected_quantity=inspected_qty,
                passed_quantity=passed_qty,
                failed_quantity=failed_qty,
                result=data.get("result", res_status),
                inspected_at=datetime.utcnow(),
                inspector_name=data.get("inspector_name", "Quality Engineer"),
                notes=data.get("notes")
            )
            session.add(insp)

            # Update production order progress
            order.completed_quantity += passed_qty
            order.scrapped_quantity += failed_qty
            if order.completed_quantity >= order.target_quantity:
                order.status = "COMPLETED"
                order.actual_end_date = datetime.utcnow()
            elif order.status == "PLANNED":
                order.status = "IN_PROGRESS"
                order.actual_start_date = datetime.utcnow()

            return insp.to_dict()
