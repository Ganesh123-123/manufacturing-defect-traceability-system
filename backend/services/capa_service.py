from datetime import datetime
from backend.database.connection import db, get_session
from backend.models import CorrectiveAction, Defect, CorrectiveActionEvent, DefectEvent
from backend.validation.exceptions import ValidationError, LifecycleViolationException
from backend.validation.rules import validate_capa_closure

class CAPAService:
    @staticmethod
    def get_capas(page=1, per_page=50, search=None, status=None):
        query = CorrectiveAction.query
        if search:
            query = query.filter(
                CorrectiveAction.id.ilike(f"%{search}%") |
                CorrectiveAction.title.ilike(f"%{search}%") |
                CorrectiveAction.defect_id.ilike(f"%{search}%")
            )
        if status:
            query = query.filter(CorrectiveAction.status == status)
        
        total = query.count()
        capas = query.order_by(CorrectiveAction.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [c.to_dict() for c in capas],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_capa(capa_id):
        capa = CorrectiveAction.query.get(capa_id)
        if not capa:
            raise ValidationError(f"Corrective Action {capa_id} not found", code="NOT_FOUND")
        res = capa.to_dict()
        res["events"] = [e.to_dict() for e in capa.events]
        res["defect"] = capa.defect.to_dict() if capa.defect else None
        return res

    @staticmethod
    def create_capa(data):
        defect_id = data.get("defect_id")
        defect = Defect.query.get(defect_id)
        if not defect_id or not defect:
            raise ValidationError(f"Valid defect_id is required. Defect {defect_id} not found.")

        capa_id = data.get("id")
        if not capa_id:
            raise ValidationError("CAPA id is required.")
        if CorrectiveAction.query.get(capa_id):
            raise ValidationError(f"Corrective Action {capa_id} already exists.", code="DUPLICATE_KEY")

        with get_session() as session:
            capa = CorrectiveAction(
                id=capa_id,
                defect_id=defect_id,
                containment_action_id=data.get("containment_action_id"),
                title=data.get("title", f"CAPA for defect {defect.defect_code}"),
                description=data.get("description", defect.description),
                root_cause_analysis=data.get("root_cause_analysis", "5-Why investigation initiated."),
                corrective_action_plan=data.get("corrective_action_plan", "Tool recalibration and operator retraining."),
                preventive_action_plan=data.get("preventive_action_plan", "Poka-yoke jig update and monthly preventive check."),
                status="OPEN",
                assigned_to=data.get("assigned_to", "Lead Quality Engineer"),
                target_date=datetime.utcnow()
            )
            session.add(capa)

            # Record event
            event = CorrectiveActionEvent(
                capa_id=capa_id,
                event_type="CREATED",
                from_status=None,
                to_status="OPEN",
                changed_by=capa.assigned_to,
                note="CAPA initiated following defect identification."
            )
            session.add(event)

            # Update defect status
            defect.status = "CAPA_INITIATED"
            def_event = DefectEvent(
                defect_id=defect_id,
                event_type="CAPA_ASSIGNED",
                from_status="CONTAINED",
                to_status="CAPA_INITIATED",
                note=f"Assigned to {capa_id}"
            )
            session.add(def_event)

            return capa.to_dict()

    @staticmethod
    def verify_capa(capa_id, data):
        capa = CorrectiveAction.query.get(capa_id)
        if not capa:
            raise ValidationError(f"Corrective Action {capa_id} not found.")

        verified_by = data.get("verified_by", "Quality Assurance Director")
        notes = data.get("verification_notes", "Verified process stabilization over 3 production runs.")

        with get_session() as session:
            old_status = capa.status
            capa.verification_date = datetime.utcnow()
            capa.verified_by = verified_by
            capa.verification_notes = notes
            capa.status = "VERIFIED"

            event = CorrectiveActionEvent(
                capa_id=capa_id,
                event_type="VERIFIED",
                from_status=old_status,
                to_status="VERIFIED",
                changed_by=verified_by,
                note=notes
            )
            session.add(event)
            return capa.to_dict()

    @staticmethod
    def close_capa(capa_id, data=None):
        capa = CorrectiveAction.query.get(capa_id)
        if not capa:
            raise ValidationError(f"Corrective Action {capa_id} not found.")

        data = data or {}
        closed_by = data.get("closed_by", "Quality Manager")
        notes = data.get("notes", "CAPA successfully resolved and validated.")

        # Rule 9 & Anomaly Scenario 3: Reject closure if not verified
        is_verified = (capa.status == "VERIFIED") or bool(capa.verification_date and capa.verified_by)
        if not is_verified:
            with get_session() as session:
                violation_event = CorrectiveActionEvent(
                    capa_id=capa_id,
                    event_type="REJECTED_CLOSURE",
                    from_status=capa.status,
                    to_status=capa.status,
                    changed_by=closed_by,
                    note="Closure rejected: Verification has not been performed."
                )
                session.add(violation_event)
            raise LifecycleViolationException(
                f"Cannot close Corrective Action {capa_id}: Formal verification must be completed before closure."
            )

        with get_session() as session:
            old_status = capa.status
            capa.status = "CLOSED"
            capa.closure_date = datetime.utcnow()

            event = CorrectiveActionEvent(
                capa_id=capa_id,
                event_type="CLOSED",
                from_status=old_status,
                to_status="CLOSED",
                changed_by=closed_by,
                note=notes
            )
            session.add(event)

            # Update linked defect status to CLOSED
            if capa.defect:
                capa.defect.status = "CLOSED"
                def_event = DefectEvent(
                    defect_id=capa.defect_id,
                    event_type="STATUS_CHANGE",
                    from_status="RESOLVED",
                    to_status="CLOSED",
                    note=f"Closed via CAPA {capa_id}"
                )
                session.add(def_event)

            return capa.to_dict()

