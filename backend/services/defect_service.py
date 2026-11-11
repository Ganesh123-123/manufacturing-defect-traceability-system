from datetime import datetime
from backend.database.connection import db, get_session
from backend.models import (
    Defect, InspectionResult, ProductionOrder, MaterialLot,
    DefectEvent, ContainmentAction, Machine, ProcessStep
)
from backend.validation.exceptions import ValidationError
from backend.validation.rules import validate_defect_quantity

class DefectService:
    @staticmethod
    def get_defects(page=1, per_page=50, search=None, severity=None, status=None, disposition=None):
        query = Defect.query
        if search:
            query = query.filter(
                Defect.id.ilike(f"%{search}%") |
                Defect.defect_code.ilike(f"%{search}%") |
                Defect.defect_type.ilike(f"%{search}%") |
                Defect.production_order_id.ilike(f"%{search}%")
            )
        if severity:
            query = query.filter(Defect.severity == severity)
        if status:
            query = query.filter(Defect.status == status)
        if disposition:
            query = query.filter(Defect.disposition == disposition)
        
        total = query.count()
        defects = query.order_by(Defect.detected_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [d.to_dict() for d in defects],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_defect(defect_id):
        defect = Defect.query.get(defect_id)
        if not defect:
            raise ValidationError(f"Defect {defect_id} not found", code="NOT_FOUND")
        res = defect.to_dict()
        res["events"] = [e.to_dict() for e in defect.events]
        res["containment_actions"] = [c.to_dict() for c in defect.containment_actions]
        res["corrective_actions"] = [ca.to_dict() for ca in defect.corrective_actions]
        return res

    @staticmethod
    def record_defect(data):
        # Rule 6: Defects must reference valid inspection results
        insp_id = data.get("inspection_result_id")
        insp = InspectionResult.query.get(insp_id)
        if not insp_id or not insp:
            raise ValidationError(f"Valid inspection_result_id is required. Inspection {insp_id} not found.")

        defect_id = data.get("id")
        if not defect_id:
            raise ValidationError("Defect id is required.")
        if Defect.query.get(defect_id):
            raise ValidationError(f"Defect {defect_id} already exists.", code="DUPLICATE_KEY")

        defect_qty = int(data.get("defect_quantity", 1))
        # Rule 7: Defect quantity must not exceed inspected quantity
        validate_defect_quantity(defect_qty, insp.inspected_quantity)

        disposition = data.get("disposition", "REWORK")
        rework_qty = defect_qty if disposition == "REWORK" else 0
        scrap_qty = defect_qty if disposition == "SCRAP" else 0

        # Validate material lot if provided
        material_lot_id = data.get("material_lot_id")
        if material_lot_id and not MaterialLot.query.get(material_lot_id):
            raise ValidationError(f"Material Lot {material_lot_id} does not exist.")

        with get_session() as session:
            defect = Defect(
                id=defect_id,
                inspection_result_id=insp_id,
                production_order_id=insp.production_order_id,
                material_lot_id=material_lot_id,
                machine_id=data.get("machine_id") or insp.machine_id,
                step_id=data.get("step_id") or insp.step_id,
                defect_code=data.get("defect_code", "GEN-001"),
                defect_type=data.get("defect_type", "General Non-conformance"),
                severity=data.get("severity", "MAJOR"),
                defect_quantity=defect_qty,
                disposition=disposition,
                rework_quantity=rework_qty,
                scrap_quantity=scrap_qty,
                root_cause_category=data.get("root_cause_category", "MATERIAL"),
                description=data.get("description", "Quality defect identified during inspection."),
                status="IDENTIFIED",
                detected_at=datetime.utcnow()
            )
            session.add(defect)

            # Record DefectEvent (Rule 12)
            event = DefectEvent(
                defect_id=defect_id,
                event_type="CREATED",
                from_status=None,
                to_status="IDENTIFIED",
                note=f"Defect recorded with disposition {disposition} (Qty: {defect_qty})."
            )
            session.add(event)

            # Update Production Order rework/scrap if applicable
            order = ProductionOrder.query.get(insp.production_order_id)
            if order:
                order.rework_quantity += rework_qty
                # scrap_quantity may already be updated by inspection or can reflect additional defect scrap

            return defect.to_dict()

    @staticmethod
    def create_containment_action(defect_id, data):
        defect = Defect.query.get(defect_id)
        if not defect:
            raise ValidationError(f"Defect {defect_id} not found.")

        with get_session() as session:
            ca = ContainmentAction(
                defect_id=defect_id,
                action_type=data.get("action_type", "LOT_QUARANTINE"),
                action_description=data.get("action_description", "Immediate lot hold and quarantine in staging area."),
                target_lot_id=data.get("target_lot_id") or defect.material_lot_id,
                quarantined_quantity=float(data.get("quarantined_quantity", 0.0)),
                status="ACTIVE",
                initiated_at=datetime.utcnow()
            )
            session.add(ca)

            # Update defect status
            old_status = defect.status
            defect.status = "CONTAINED"

            event = DefectEvent(
                defect_id=defect_id,
                event_type="CONTAINMENT_TRIGGERED",
                from_status=old_status,
                to_status="CONTAINED",
                note=f"Containment action initiated: {ca.action_type}"
            )
            session.add(event)

            # If target lot specified, update lot status to QUARANTINED
            if ca.target_lot_id:
                lot = MaterialLot.query.get(ca.target_lot_id)
                if lot:
                    lot.status = "QUARANTINED"

            session.flush()
            return ca.to_dict()

