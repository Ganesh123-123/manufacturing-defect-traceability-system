from backend.generator.data_factory import DataFactory
from backend.generator.anomaly_injector import AnomalyInjector
from backend.validation.rules import (
    validate_defect_quantity,
    validate_inspection_quantities,
    validate_capa_closure,
    run_full_database_validation
)
from backend.validation.exceptions import (
    QuantityValidationException,
    LifecycleViolationException
)
from backend.database.connection import db
from backend.models import (
    Product, Supplier, MaterialLot, ProductionOrder, BOM, Machine,
    ProcessStep, ProcessStepMachine, InspectionPlan, InspectionResult,
    Defect, ContainmentAction, CorrectiveAction, MaterialConsumption,
    ProductionOrderMaterial, ProductionEvent, DefectEvent, CorrectiveActionEvent
)

def test_anomaly_scenario_1_broken_lot_reference(db_session):
    # Defect links to nonexistent material lot
    p = Product(id="SKU-000001", name="Test Prod", category="Test")
    s = Supplier(id="SUP-000001", name="Test Sup", code="SUP-001")
    po = ProductionOrder(id="WO-2026-000001", product_id="SKU-000001", target_quantity=100)
    ip = InspectionPlan(id="IP-01", product_id="SKU-000001", name="Test Plan")
    insp = InspectionResult(id="INSP-01", inspection_plan_id="IP-01", production_order_id="WO-2026-000001", inspected_quantity=10, passed_quantity=9, failed_quantity=1)
    
    # Injected anomaly: invalid lot
    defect = Defect(
        id="DEF-ANOM-01",
        inspection_result_id="INSP-01",
        production_order_id="WO-2026-000001",
        material_lot_id="LOT-SUP-999999-2026-999999",
        defect_code="ERR-01",
        defect_type="Broken Lot Ref",
        severity="CRITICAL",
        defect_quantity=1
    )
    db_session.add_all([p, s, po, ip, insp, defect])
    db_session.commit()

    summary = run_full_database_validation(db_session)
    anom_ids = [a.get("anomaly_id") for a in summary["detected_anomalies"]]
    assert "SCENARIO_1" in anom_ids

def test_anomaly_scenario_2_bom_material_not_consumed(db_session):
    # BOM exists for product, but order is COMPLETED with 0 consumption recorded
    p = Product(id="SKU-000002", name="Prod 2", category="Test")
    bom = BOM(id=99, parent_product_id="SKU-000002", component_sku="MAT-MANDATORY", component_name="Crucial Wire", quantity_per_unit=1.0)
    po = ProductionOrder(id="WO-2026-000002", product_id="SKU-000002", target_quantity=50, status="COMPLETED")
    
    db_session.add_all([p, bom, po])
    db_session.commit()

    summary = run_full_database_validation(db_session)
    anom_ids = [a.get("anomaly_id") for a in summary["detected_anomalies"]]
    assert "SCENARIO_2" in anom_ids

def test_anomaly_scenario_3_capa_closed_without_verification(db_session):
    # Rule 9 / Scenario 3: CAPA closed without verification must raise LifecycleViolationException
    try:
        validate_capa_closure(status_to="CLOSED", is_verified=False, verification_date=None, verified_by=None)
        assert False, "Should have raised LifecycleViolationException"
    except LifecycleViolationException as e:
        assert "verification" in str(e).lower()

    # In database audit
    p = Product(id="SKU-000003", name="Prod 3", category="Test")
    po = ProductionOrder(id="WO-2026-000003", product_id="SKU-000003", target_quantity=10)
    ip = InspectionPlan(id="IP-03", product_id="SKU-000003", name="Plan 3")
    insp = InspectionResult(id="INSP-03", inspection_plan_id="IP-03", production_order_id="WO-2026-000003", inspected_quantity=10, passed_quantity=9, failed_quantity=1)
    defect = Defect(id="DEF-03", inspection_result_id="INSP-03", production_order_id="WO-2026-000003", defect_code="D3", defect_type="T3", severity="MAJOR", defect_quantity=1)
    
    # Injected premature closure in DB
    capa = CorrectiveAction(
        id="CAPA-ANOM-03",
        defect_id="DEF-03",
        title="Unverified CAPA",
        status="CLOSED",
        verification_date=None,
        verified_by=None
    )
    db_session.add_all([p, po, ip, insp, defect, capa])
    db_session.commit()

    summary = run_full_database_validation(db_session)
    anom_ids = [a.get("anomaly_id") for a in summary["detected_anomalies"]]
    assert "SCENARIO_3" in anom_ids

def test_anomaly_scenario_4_defect_exceeds_inspected(db_session):
    # Defect count > Inspected quantity
    try:
        validate_defect_quantity(defect_qty=25, inspected_qty=10)
        assert False, "Should have raised QuantityValidationException"
    except QuantityValidationException as e:
        assert "exceed" in str(e).lower()

    p = Product(id="SKU-000004", name="Prod 4", category="Test")
    po = ProductionOrder(id="WO-2026-000004", product_id="SKU-000004", target_quantity=10)
    ip = InspectionPlan(id="IP-04", product_id="SKU-000004", name="Plan 4")
    insp = InspectionResult(id="INSP-04", inspection_plan_id="IP-04", production_order_id="WO-2026-000004", inspected_quantity=10, passed_quantity=0, failed_quantity=10)
    defect = Defect(
        id="DEF-ANOM-04",
        inspection_result_id="INSP-04",
        production_order_id="WO-2026-000004",
        defect_code="D4",
        defect_type="Excess Defect",
        severity="CRITICAL",
        defect_quantity=25  # Exceeds 10
    )
    db_session.add_all([p, po, ip, insp, defect])
    db_session.commit()

    summary = run_full_database_validation(db_session)
    anom_ids = [a.get("anomaly_id") for a in summary["detected_anomalies"]]
    assert "SCENARIO_4" in anom_ids

def test_anomaly_scenario_5_broken_traceability_chain(db_session):
    # Defect has non-existent production order
    p = Product(id="SKU-000005", name="Prod 5", category="Test")
    ip = InspectionPlan(id="IP-05", product_id="SKU-000005", name="Plan 5")
    defect = Defect(
        id="DEF-ANOM-05",
        inspection_result_id="INSP-NONEXISTENT",
        production_order_id="WO-2026-999999",  # Broken order
        defect_code="D5",
        defect_type="Disconnected defect",
        severity="CRITICAL",
        defect_quantity=1
    )
    db_session.add_all([p, ip, defect])
    db_session.commit()

    summary = run_full_database_validation(db_session)
    anom_ids = [a.get("anomaly_id") for a in summary["detected_anomalies"]]
    assert "SCENARIO_5" in anom_ids
