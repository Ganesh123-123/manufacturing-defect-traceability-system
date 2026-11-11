import logging
from backend.time_utils import utcnow
from backend.validation.exceptions import (
    ValidationError,
    LifecycleViolationException,
    MaterialReconciliationException,
    QuantityValidationException,
    TraceabilityBrokenException
)

logger = logging.getLogger(__name__)

def validate_inspection_quantities(inspected_qty, passed_qty, failed_qty):
    """Rule 7 & 11: Defect / inspection quantity integrity."""
    if inspected_qty <= 0:
        raise QuantityValidationException("Inspected quantity must be strictly greater than 0.")
    if passed_qty < 0 or failed_qty < 0:
        raise QuantityValidationException("Passed and failed quantities cannot be negative.")
    if passed_qty + failed_qty != inspected_qty:
        raise QuantityValidationException(
            f"Inspection sum mismatch: passed ({passed_qty}) + failed ({failed_qty}) must equal inspected ({inspected_qty})."
        )
    return True

def validate_defect_quantity(defect_qty, inspected_qty):
    """Rule 7: Defect quantity must not exceed inspected quantity."""
    if defect_qty <= 0:
        raise QuantityValidationException("Defect quantity must be greater than 0.")
    if defect_qty > inspected_qty:
        raise QuantityValidationException(
            f"Defect quantity ({defect_qty}) cannot exceed inspected quantity ({inspected_qty})."
        )
    return True

def validate_capa_closure(status_to, is_verified, verification_date, verified_by):
    """Rule 9: Corrective actions cannot close before verification."""
    if status_to == "CLOSED":
        if not is_verified or not verification_date or not verified_by:
            raise LifecycleViolationException(
                "Lifecycle violation: Corrective action cannot be CLOSED before formal verification is completed."
            )
    return True

def validate_material_consumption_reconciliation(required_qty, consumed_qty, tolerance=0.25):
    """Rule 4: Material consumption must reconcile with BOM requirements."""
    if consumed_qty <= 0:
        raise MaterialReconciliationException("Consumed quantity must be greater than 0.")
    min_allowed = required_qty * (1.0 - tolerance)
    max_allowed = required_qty * (1.0 + tolerance)
    if consumed_qty < min_allowed or consumed_qty > max_allowed:
        raise MaterialReconciliationException(
            f"Material consumption ({consumed_qty}) deviates beyond allowed tolerance from BOM required ({required_qty})."
        )
    return True

def run_full_database_validation(db_session):
    """
    Executes a comprehensive audit of all database entities, foreign keys,
    traceability chains, quantity bounds, lifecycle rules, and anomaly detections.
    Returns a structured dictionary matching validation_summary.json.
    """
    from backend.models import (
        Product, Supplier, MaterialLot, ProductionOrder, BOM, Machine,
        ProcessStep, InspectionPlan, InspectionResult, Defect,
        CorrectiveAction, MaterialConsumption
    )

    total_checks = 0
    passed_checks = 0
    failed_checks = 0
    detected_anomalies = []

    # 1. Count records
    counts = {
        "products": db_session.query(Product).count(),
        "suppliers": db_session.query(Supplier).count(),
        "material_lots": db_session.query(MaterialLot).count(),
        "production_orders": db_session.query(ProductionOrder).count(),
        "boms": db_session.query(BOM).count(),
        "machines": db_session.query(Machine).count(),
        "process_steps": db_session.query(ProcessStep).count(),
        "inspection_plans": db_session.query(InspectionPlan).count(),
        "inspection_results": db_session.query(InspectionResult).count(),
        "defects": db_session.query(Defect).count(),
        "corrective_actions": db_session.query(CorrectiveAction).count(),
        "material_consumptions": db_session.query(MaterialConsumption).count(),
    }
    total_records = sum(counts.values())

    # 2. Check Foreign Keys and Orphan Records
    # Check MaterialLot -> Supplier
    lots = db_session.query(MaterialLot).all()
    valid_supplier_ids = {s.id for s in db_session.query(Supplier.id).all()}
    for lot in lots:
        total_checks += 1
        if lot.supplier_id not in valid_supplier_ids:
            failed_checks += 1
            detected_anomalies.append({
                "check": "foreign_key_supplier",
                "entity": "MaterialLot",
                "record_id": lot.id,
                "detail": f"MaterialLot {lot.id} references invalid supplier {lot.supplier_id}"
            })
        else:
            passed_checks += 1

    # Check ProductionOrder -> Product
    orders = db_session.query(ProductionOrder).all()
    valid_product_ids = {p.id for p in db_session.query(Product.id).all()}
    for order in orders:
        total_checks += 1
        if order.product_id not in valid_product_ids:
            failed_checks += 1
            detected_anomalies.append({
                "check": "foreign_key_product",
                "entity": "ProductionOrder",
                "record_id": order.id,
                "detail": f"ProductionOrder {order.id} references invalid product {order.product_id}"
            })
        else:
            passed_checks += 1

    # Check Defect -> MaterialLot (Anomaly Scenario 1)
    defects = db_session.query(Defect).all()
    valid_lot_ids = {l.id for l in db_session.query(MaterialLot.id).all()}
    for defect in defects:
        total_checks += 1
        if defect.material_lot_id and defect.material_lot_id not in valid_lot_ids:
            failed_checks += 1
            detected_anomalies.append({
                "anomaly_id": "SCENARIO_1",
                "check": "broken_foreign_key_lot",
                "entity": "Defect",
                "record_id": defect.id,
                "detail": f"Defect references non-existent material lot: {defect.material_lot_id}",
                "severity": "CRITICAL"
            })
        else:
            passed_checks += 1

    # Check Inspection Quantities (Anomaly Scenario 4)
    inspections = db_session.query(InspectionResult).all()
    insp_map = {i.id: i for i in inspections}
    for insp in inspections:
        total_checks += 1
        if insp.passed_quantity + insp.failed_quantity != insp.inspected_quantity:
            failed_checks += 1
            detected_anomalies.append({
                "check": "inspection_quantity_sum",
                "entity": "InspectionResult",
                "record_id": insp.id,
                "detail": f"Inspection sum mismatch: {insp.passed_quantity} + {insp.failed_quantity} != {insp.inspected_quantity}"
            })
        else:
            passed_checks += 1

    # Check Defect count <= Inspected count (Anomaly Scenario 4)
    for defect in defects:
        total_checks += 1
        insp = insp_map.get(defect.inspection_result_id)
        if insp and defect.defect_quantity > insp.inspected_quantity:
            failed_checks += 1
            detected_anomalies.append({
                "anomaly_id": "SCENARIO_4",
                "check": "defect_exceeds_inspected",
                "entity": "Defect",
                "record_id": defect.id,
                "detail": f"Defect quantity ({defect.defect_quantity}) exceeds inspected quantity ({insp.inspected_quantity})",
                "severity": "CRITICAL"
            })
        else:
            passed_checks += 1

    # Check CAPA Verification Lifecycle (Anomaly Scenario 3)
    capas = db_session.query(CorrectiveAction).all()
    for capa in capas:
        total_checks += 1
        if capa.status == "CLOSED" and (not capa.verification_date or not capa.verified_by):
            failed_checks += 1
            detected_anomalies.append({
                "anomaly_id": "SCENARIO_3",
                "check": "capa_closure_without_verification",
                "entity": "CorrectiveAction",
                "record_id": capa.id,
                "detail": f"CAPA {capa.id} was marked CLOSED without formal verification record",
                "severity": "MAJOR"
            })
        else:
            passed_checks += 1

    # Check BOM Material Consumed (Anomaly Scenario 2)
    # For completed or in-progress orders, ensure required BOM items have at least one consumption
    order_consumptions = {}
    for c in db_session.query(MaterialConsumption).all():
        order_consumptions.setdefault(c.production_order_id, set()).add(c.bom_id)

    boms_by_product = {}
    for b in db_session.query(BOM).all():
        boms_by_product.setdefault(b.parent_product_id, []).append(b)

    for order in orders:
        if order.status in ("COMPLETED", "IN_PROGRESS"):
            expected_boms = boms_by_product.get(order.product_id, [])
            consumed_boms = order_consumptions.get(order.id, set())
            for eb in expected_boms:
                total_checks += 1
                if eb.id not in consumed_boms:
                    failed_checks += 1
                    detected_anomalies.append({
                        "anomaly_id": "SCENARIO_2",
                        "check": "bom_material_not_consumed",
                        "entity": "ProductionOrder",
                        "record_id": order.id,
                        "detail": f"BOM component {eb.component_name} ({eb.component_sku}) not consumed for order {order.id}",
                        "severity": "HIGH"
                    })
                else:
                    passed_checks += 1

    # Check Traceability Chain Integrity (Anomaly Scenario 5)
    # Check if defect can trace back to production order and product
    for defect in defects:
        total_checks += 1
        if not defect.production_order_id or defect.production_order_id not in {o.id for o in orders}:
            failed_checks += 1
            detected_anomalies.append({
                "anomaly_id": "SCENARIO_5",
                "check": "broken_traceability_chain",
                "entity": "Defect",
                "record_id": defect.id,
                "detail": f"Defect {defect.id} has disconnected production order link",
                "severity": "CRITICAL"
            })
        else:
            passed_checks += 1

    validation_status = "PASSED" if failed_checks == 0 else "ANOMALIES_DETECTED"

    summary = {
        "timestamp": utcnow().isoformat(),
        "total_records": total_records,
        "entity_counts": counts,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "validation_status": validation_status,
        "detected_anomalies_count": len(detected_anomalies),
        "detected_anomalies": detected_anomalies
    }
    return summary
