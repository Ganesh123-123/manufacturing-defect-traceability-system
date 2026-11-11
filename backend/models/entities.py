from backend.time_utils import utcnow
from backend.database.connection import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.String(32), primary_key=True)  # SKU-000001
    name = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    unit_of_measure = db.Column(db.String(20), default="PCS")
    target_cycle_time_mins = db.Column(db.Float, default=15.0)
    standard_cost = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    boms = db.relationship("BOM", backref="product", lazy=True, cascade="all, delete-orphan")
    production_orders = db.relationship("ProductionOrder", backref="product", lazy=True)
    inspection_plans = db.relationship("InspectionPlan", backref="product", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "unit_of_measure": self.unit_of_measure,
            "target_cycle_time_mins": self.target_cycle_time_mins,
            "standard_cost": self.standard_cost,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "bom_items_count": len(self.boms) if self.boms else 0
        }


class BOM(db.Model):
    __tablename__ = "boms"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_product_id = db.Column(db.String(32), db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    component_sku = db.Column(db.String(64), nullable=False, index=True)
    component_name = db.Column(db.String(150), nullable=False)
    quantity_per_unit = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(20), default="PCS")
    scrap_factor = db.Column(db.Float, default=0.0)
    effective_from = db.Column(db.DateTime, nullable=False, default=utcnow)
    effective_to = db.Column(db.DateTime, nullable=True)
    revision = db.Column(db.String(20), default="1.0")
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "parent_product_id": self.parent_product_id,
            "component_sku": self.component_sku,
            "component_name": self.component_name,
            "quantity_per_unit": self.quantity_per_unit,
            "unit_of_measure": self.unit_of_measure,
            "scrap_factor": self.scrap_factor,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "effective_to": self.effective_to.isoformat() if self.effective_to else None,
            "revision": self.revision,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.String(32), primary_key=True)  # SUP-000001
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(50))
    country = db.Column(db.String(80), default="USA")
    rating = db.Column(db.Float, default=4.5)
    status = db.Column(db.String(30), default="ACTIVE")  # ACTIVE, APPROVED, ON_PROBATION, SUSPENDED
    created_at = db.Column(db.DateTime, default=utcnow)

    material_lots = db.relationship("MaterialLot", backref="supplier", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "country": self.country,
            "rating": self.rating,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "material_lots_count": len(self.material_lots) if self.material_lots else 0
        }


class MaterialLot(db.Model):
    __tablename__ = "material_lots"

    id = db.Column(db.String(64), primary_key=True)  # LOT-SUP-000001-2026-000001
    supplier_id = db.Column(db.String(32), db.ForeignKey("suppliers.id"), nullable=False, index=True)
    material_sku = db.Column(db.String(64), nullable=False, index=True)
    material_name = db.Column(db.String(150), nullable=False)
    batch_number = db.Column(db.String(64), nullable=False)
    initial_quantity = db.Column(db.Float, nullable=False)
    remaining_quantity = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(20), default="PCS")
    received_date = db.Column(db.DateTime, nullable=False, default=utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    certificate_of_analysis = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), default="RELEASED")  # RECEIVED, QUARANTINED, RELEASED, CONSUMED, REJECTED
    created_at = db.Column(db.DateTime, default=utcnow)

    consumptions = db.relationship("MaterialConsumption", backref="material_lot", lazy=True)
    defects = db.relationship("Defect", backref="material_lot", lazy=True)
    containment_actions = db.relationship("ContainmentAction", backref="material_lot", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else None,
            "material_sku": self.material_sku,
            "material_name": self.material_name,
            "batch_number": self.batch_number,
            "initial_quantity": self.initial_quantity,
            "remaining_quantity": self.remaining_quantity,
            "unit_of_measure": self.unit_of_measure,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "certificate_of_analysis": self.certificate_of_analysis,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProductionOrder(db.Model):
    __tablename__ = "production_orders"

    id = db.Column(db.String(32), primary_key=True)  # WO-2026-000001
    product_id = db.Column(db.String(32), db.ForeignKey("products.id"), nullable=False, index=True)
    target_quantity = db.Column(db.Integer, nullable=False)
    completed_quantity = db.Column(db.Integer, default=0)
    scrapped_quantity = db.Column(db.Integer, default=0)
    rework_quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default="PLANNED", index=True)  # PLANNED, RELEASED, IN_PROGRESS, COMPLETED, ON_HOLD, CANCELLED
    planned_start_date = db.Column(db.DateTime, nullable=True)
    planned_end_date = db.Column(db.DateTime, nullable=True)
    actual_start_date = db.Column(db.DateTime, nullable=True)
    actual_end_date = db.Column(db.DateTime, nullable=True)
    batch_number = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    consumptions = db.relationship("MaterialConsumption", backref="production_order", lazy=True)
    inspections = db.relationship("InspectionResult", backref="production_order", lazy=True)
    production_events = db.relationship("ProductionEvent", backref="production_order", lazy=True)
    defects = db.relationship("Defect", backref="production_order", lazy=True)
    planned_materials = db.relationship("ProductionOrderMaterial", backref="production_order", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "target_quantity": self.target_quantity,
            "completed_quantity": self.completed_quantity,
            "scrapped_quantity": self.scrapped_quantity,
            "rework_quantity": self.rework_quantity,
            "status": self.status,
            "planned_start_date": self.planned_start_date.isoformat() if self.planned_start_date else None,
            "planned_end_date": self.planned_end_date.isoformat() if self.planned_end_date else None,
            "actual_start_date": self.actual_start_date.isoformat() if self.actual_start_date else None,
            "actual_end_date": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "batch_number": self.batch_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "consumptions_count": len(self.consumptions) if self.consumptions else 0,
            "inspections_count": len(self.inspections) if self.inspections else 0
        }


class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(db.String(32), primary_key=True)  # MAC-001
    machine_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(60), nullable=False)
    line = db.Column(db.String(50), nullable=False, index=True)
    location = db.Column(db.String(80))
    status = db.Column(db.String(30), default="OPERATIONAL")  # OPERATIONAL, MAINTENANCE, OFFLINE, DECOMMISSIONED
    calibration_due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    step_machines = db.relationship("ProcessStepMachine", backref="machine", lazy=True)
    inspections = db.relationship("InspectionResult", backref="machine", lazy=True)
    defects = db.relationship("Defect", backref="machine", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "machine_code": self.machine_code,
            "name": self.name,
            "type": self.type,
            "line": self.line,
            "location": self.location,
            "status": self.status,
            "calibration_due_date": self.calibration_due_date.isoformat() if self.calibration_due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProcessStep(db.Model):
    __tablename__ = "process_steps"

    id = db.Column(db.String(32), primary_key=True)  # STEP-010
    step_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False, index=True)
    standard_duration_mins = db.Column(db.Float, default=10.0)
    inspection_required = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    step_machines = db.relationship("ProcessStepMachine", backref="process_step", lazy=True)
    inspection_plans = db.relationship("InspectionPlan", backref="process_step", lazy=True)
    inspections = db.relationship("InspectionResult", backref="process_step", lazy=True)
    defects = db.relationship("Defect", backref="process_step", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "step_code": self.step_code,
            "name": self.name,
            "sequence_number": self.sequence_number,
            "standard_duration_mins": self.standard_duration_mins,
            "inspection_required": self.inspection_required,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProcessStepMachine(db.Model):
    __tablename__ = "process_step_machines"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    step_id = db.Column(db.String(32), db.ForeignKey("process_steps.id"), nullable=False)
    machine_id = db.Column(db.String(32), db.ForeignKey("machines.id"), nullable=False)
    is_primary = db.Column(db.Boolean, default=True)
    setup_time_mins = db.Column(db.Float, default=15.0)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "step_id": self.step_id,
            "machine_id": self.machine_id,
            "is_primary": self.is_primary,
            "setup_time_mins": self.setup_time_mins,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class InspectionPlan(db.Model):
    __tablename__ = "inspection_plans"

    id = db.Column(db.String(64), primary_key=True)  # IP-SKU-000001-01
    product_id = db.Column(db.String(32), db.ForeignKey("products.id"), nullable=False, index=True)
    step_id = db.Column(db.String(32), db.ForeignKey("process_steps.id"), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    sampling_type = db.Column(db.String(30), default="SAMPLE")  # 100_PERCENT, SAMPLE, AQL_NORMAL
    sample_size_percentage = db.Column(db.Float, default=10.0)
    tolerance_critical = db.Column(db.Float, default=0.0)
    tolerance_major = db.Column(db.Float, default=1.0)
    tolerance_minor = db.Column(db.Float, default=2.5)
    criteria = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    inspection_results = db.relationship("InspectionResult", backref="inspection_plan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "step_id": self.step_id,
            "step_name": self.process_step.name if self.process_step else None,
            "name": self.name,
            "sampling_type": self.sampling_type,
            "sample_size_percentage": self.sample_size_percentage,
            "tolerance_critical": self.tolerance_critical,
            "tolerance_major": self.tolerance_major,
            "tolerance_minor": self.tolerance_minor,
            "criteria": self.criteria,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class InspectionResult(db.Model):
    __tablename__ = "inspection_results"

    id = db.Column(db.String(64), primary_key=True)  # INSP-WO-2026-000001-001
    inspection_plan_id = db.Column(db.String(64), db.ForeignKey("inspection_plans.id"), nullable=False, index=True)
    production_order_id = db.Column(db.String(32), db.ForeignKey("production_orders.id"), nullable=False, index=True)
    step_id = db.Column(db.String(32), db.ForeignKey("process_steps.id"), nullable=True, index=True)
    machine_id = db.Column(db.String(32), db.ForeignKey("machines.id"), nullable=True, index=True)
    inspected_quantity = db.Column(db.Integer, nullable=False)
    passed_quantity = db.Column(db.Integer, nullable=False, default=0)
    failed_quantity = db.Column(db.Integer, nullable=False, default=0)
    result = db.Column(db.String(30), default="PASS", index=True)  # PASS, FAIL, CONDITIONAL_PASS
    inspected_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    inspector_name = db.Column(db.String(100), default="Quality Inspector")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    defects = db.relationship("Defect", backref="inspection_result", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "inspection_plan_id": self.inspection_plan_id,
            "production_order_id": self.production_order_id,
            "step_id": self.step_id,
            "step_name": self.process_step.name if self.process_step else None,
            "machine_id": self.machine_id,
            "machine_name": self.machine.name if self.machine else None,
            "inspected_quantity": self.inspected_quantity,
            "passed_quantity": self.passed_quantity,
            "failed_quantity": self.failed_quantity,
            "result": self.result,
            "inspected_at": self.inspected_at.isoformat() if self.inspected_at else None,
            "inspector_name": self.inspector_name,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "defects_count": len(self.defects) if self.defects else 0
        }


class Defect(db.Model):
    __tablename__ = "defects"

    id = db.Column(db.String(32), primary_key=True)  # DEF-2026-000001
    inspection_result_id = db.Column(db.String(64), db.ForeignKey("inspection_results.id"), nullable=False, index=True)
    production_order_id = db.Column(db.String(32), db.ForeignKey("production_orders.id"), nullable=False, index=True)
    material_lot_id = db.Column(db.String(64), db.ForeignKey("material_lots.id"), nullable=True, index=True)
    machine_id = db.Column(db.String(32), db.ForeignKey("machines.id"), nullable=True, index=True)
    step_id = db.Column(db.String(32), db.ForeignKey("process_steps.id"), nullable=True, index=True)
    defect_code = db.Column(db.String(32), nullable=False, index=True)
    defect_type = db.Column(db.String(80), nullable=False)
    severity = db.Column(db.String(20), nullable=False, index=True)  # CRITICAL, MAJOR, MINOR
    defect_quantity = db.Column(db.Integer, nullable=False)
    disposition = db.Column(db.String(30), default="REWORK")  # REWORK, SCRAP, USE_AS_IS, RETURN_TO_VENDOR
    rework_quantity = db.Column(db.Integer, default=0)
    scrap_quantity = db.Column(db.Integer, default=0)
    root_cause_category = db.Column(db.String(50), default="MATERIAL")  # MATERIAL, MACHINE, METHOD, MANPOWER, ENVIRONMENT
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="IDENTIFIED", index=True)  # IDENTIFIED, CONTAINED, UNDER_INVESTIGATION, CAPA_INITIATED, RESOLVED, CLOSED
    detected_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)

    corrective_actions = db.relationship("CorrectiveAction", backref="defect", lazy=True)
    containment_actions = db.relationship("ContainmentAction", backref="defect", lazy=True)
    events = db.relationship("DefectEvent", backref="defect", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "inspection_result_id": self.inspection_result_id,
            "production_order_id": self.production_order_id,
            "product_id": self.production_order.product_id if self.production_order else None,
            "product_name": self.production_order.product.name if self.production_order and self.production_order.product else None,
            "material_lot_id": self.material_lot_id,
            "supplier_id": self.material_lot.supplier_id if self.material_lot else None,
            "supplier_name": self.material_lot.supplier.name if self.material_lot and self.material_lot.supplier else None,
            "machine_id": self.machine_id,
            "machine_name": self.machine.name if self.machine else None,
            "step_id": self.step_id,
            "step_name": self.process_step.name if self.process_step else None,
            "defect_code": self.defect_code,
            "defect_type": self.defect_type,
            "severity": self.severity,
            "defect_quantity": self.defect_quantity,
            "disposition": self.disposition,
            "rework_quantity": self.rework_quantity,
            "scrap_quantity": self.scrap_quantity,
            "root_cause_category": self.root_cause_category,
            "description": self.description,
            "status": self.status,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "has_capa": len(self.corrective_actions) > 0 if self.corrective_actions else False,
            "capa_id": self.corrective_actions[0].id if self.corrective_actions else None
        }


class ContainmentAction(db.Model):
    __tablename__ = "containment_actions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    defect_id = db.Column(db.String(32), db.ForeignKey("defects.id"), nullable=False, index=True)
    action_type = db.Column(db.String(50), default="LOT_QUARANTINE")  # LOT_QUARANTINE, LINE_STOP, PURGE_WIP, SORT_INSPECTION
    action_description = db.Column(db.Text, nullable=False)
    target_lot_id = db.Column(db.String(64), db.ForeignKey("material_lots.id"), nullable=True)
    quarantined_quantity = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="ACTIVE")  # ACTIVE, COMPLETED, CANCELLED
    initiated_at = db.Column(db.DateTime, default=utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "defect_id": self.defect_id,
            "action_type": self.action_type,
            "action_description": self.action_description,
            "target_lot_id": self.target_lot_id,
            "quarantined_quantity": self.quarantined_quantity,
            "status": self.status,
            "initiated_at": self.initiated_at.isoformat() if self.initiated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class CorrectiveAction(db.Model):
    __tablename__ = "corrective_actions"

    id = db.Column(db.String(32), primary_key=True)  # CAPA-2026-000001
    defect_id = db.Column(db.String(32), db.ForeignKey("defects.id"), nullable=False, index=True)
    containment_action_id = db.Column(db.Integer, db.ForeignKey("containment_actions.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    root_cause_analysis = db.Column(db.Text, nullable=True)
    corrective_action_plan = db.Column(db.Text, nullable=True)
    preventive_action_plan = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="OPEN", index=True)  # OPEN, IN_PROGRESS, CONTAINMENT, PENDING_VERIFICATION, VERIFIED, CLOSED
    assigned_to = db.Column(db.String(100), nullable=True)
    target_date = db.Column(db.DateTime, nullable=True)
    verification_date = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.String(100), nullable=True)
    verification_notes = db.Column(db.Text, nullable=True)
    closure_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    events = db.relationship("CorrectiveActionEvent", backref="corrective_action", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "defect_id": self.defect_id,
            "containment_action_id": self.containment_action_id,
            "title": self.title,
            "description": self.description,
            "root_cause_analysis": self.root_cause_analysis,
            "corrective_action_plan": self.corrective_action_plan,
            "preventive_action_plan": self.preventive_action_plan,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None,
            "verified_by": self.verified_by,
            "verification_notes": self.verification_notes,
            "closure_date": self.closure_date.isoformat() if self.closure_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MaterialConsumption(db.Model):
    __tablename__ = "material_consumptions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    production_order_id = db.Column(db.String(32), db.ForeignKey("production_orders.id"), nullable=False, index=True)
    material_lot_id = db.Column(db.String(64), db.ForeignKey("material_lots.id"), nullable=False, index=True)
    bom_id = db.Column(db.Integer, db.ForeignKey("boms.id"), nullable=True)
    consumed_quantity = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(20), default="PCS")
    consumed_at = db.Column(db.DateTime, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)

    bom = db.relationship("BOM", backref="consumptions", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "production_order_id": self.production_order_id,
            "material_lot_id": self.material_lot_id,
            "material_name": self.material_lot.material_name if self.material_lot else None,
            "bom_id": self.bom_id,
            "consumed_quantity": self.consumed_quantity,
            "unit_of_measure": self.unit_of_measure,
            "consumed_at": self.consumed_at.isoformat() if self.consumed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProductionOrderMaterial(db.Model):
    __tablename__ = "production_order_materials"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    production_order_id = db.Column(db.String(32), db.ForeignKey("production_orders.id"), nullable=False, index=True)
    bom_id = db.Column(db.Integer, db.ForeignKey("boms.id"), nullable=True)
    material_sku = db.Column(db.String(64), nullable=False)
    required_quantity = db.Column(db.Float, nullable=False)
    allocated_quantity = db.Column(db.Float, default=0.0)
    consumed_quantity = db.Column(db.Float, default=0.0)
    unit_of_measure = db.Column(db.String(20), default="PCS")
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "production_order_id": self.production_order_id,
            "bom_id": self.bom_id,
            "material_sku": self.material_sku,
            "required_quantity": self.required_quantity,
            "allocated_quantity": self.allocated_quantity,
            "consumed_quantity": self.consumed_quantity,
            "unit_of_measure": self.unit_of_measure,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProductionEvent(db.Model):
    __tablename__ = "production_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    production_order_id = db.Column(db.String(32), db.ForeignKey("production_orders.id"), nullable=False, index=True)
    step_id = db.Column(db.String(32), db.ForeignKey("process_steps.id"), nullable=True)
    machine_id = db.Column(db.String(32), db.ForeignKey("machines.id"), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # CREATED, STARTED, STEP_START, STEP_COMPLETE, COMPLETED, PAUSED
    status_from = db.Column(db.String(30))
    status_to = db.Column(db.String(30))
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "production_order_id": self.production_order_id,
            "step_id": self.step_id,
            "machine_id": self.machine_id,
            "event_type": self.event_type,
            "status_from": self.status_from,
            "status_to": self.status_to,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class DefectEvent(db.Model):
    __tablename__ = "defect_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    defect_id = db.Column(db.String(32), db.ForeignKey("defects.id"), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    from_status = db.Column(db.String(30))
    to_status = db.Column(db.String(30))
    note = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "defect_id": self.defect_id,
            "event_type": self.event_type,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "note": self.note,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class CorrectiveActionEvent(db.Model):
    __tablename__ = "corrective_action_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    capa_id = db.Column(db.String(32), db.ForeignKey("corrective_actions.id"), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    from_status = db.Column(db.String(30))
    to_status = db.Column(db.String(30))
    changed_by = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "capa_id": self.capa_id,
            "event_type": self.event_type,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "changed_by": self.changed_by,
            "note": self.note,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
