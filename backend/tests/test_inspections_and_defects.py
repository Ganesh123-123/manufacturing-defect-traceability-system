def test_inspection_and_defect_workflow(client):
    # Setup master data
    client.post("/api/products", json={"id": "SKU-000001", "name": "Precision Valve", "category": "Hydraulics"})
    client.post("/api/suppliers", json={"id": "SUP-000001", "name": "Forging Partner", "code": "SUP-FORGE"})
    client.post("/api/material-lots", json={
        "id": "LOT-SUP-000001-2026-000001",
        "supplier_id": "SUP-000001",
        "material_sku": "MAT-STEEL",
        "material_name": "Forged Steel Billet",
        "initial_quantity": 2000.0
    })
    client.post("/api/production-orders", json={
        "id": "WO-2026-000001",
        "product_id": "SKU-000001",
        "target_quantity": 100
    })

    # Create Inspection Plan
    plan_res = client.post("/api/inspection-plans", json={
        "id": "IP-SKU-000001-01",
        "product_id": "SKU-000001",
        "name": "Gate-1 Visual & CMM Plan"
    })
    assert plan_res.status_code == 201

    # Record Inspection with sum mismatch (must fail)
    mismatch_res = client.post("/api/inspections", json={
        "id": "INSP-WO-2026-000001-001",
        "inspection_plan_id": "IP-SKU-000001-01",
        "production_order_id": "WO-2026-000001",
        "inspected_quantity": 50,
        "passed_quantity": 40,
        "failed_quantity": 5  # 40 + 5 != 50
    })
    assert mismatch_res.status_code == 400

    # Record valid inspection
    insp_res = client.post("/api/inspections", json={
        "id": "INSP-WO-2026-000001-001",
        "inspection_plan_id": "IP-SKU-000001-01",
        "production_order_id": "WO-2026-000001",
        "inspected_quantity": 50,
        "passed_quantity": 46,
        "failed_quantity": 4,
        "result": "FAIL"
    })
    assert insp_res.status_code == 201

    # Record Defect with quantity exceeding inspected quantity (must fail)
    over_def_res = client.post("/api/defects", json={
        "id": "DEF-2026-000001",
        "inspection_result_id": "INSP-WO-2026-000001-001",
        "defect_code": "DIM-001",
        "defect_type": "Out of spec",
        "severity": "MAJOR",
        "defect_quantity": 60  # > 50 inspected
    })
    assert over_def_res.status_code == 400

    # Record valid Defect
    def_res = client.post("/api/defects", json={
        "id": "DEF-2026-000001",
        "inspection_result_id": "INSP-WO-2026-000001-001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "defect_code": "DIM-001",
        "defect_type": "Bore Diameter Deviation",
        "severity": "MAJOR",
        "defect_quantity": 4,
        "disposition": "REWORK",
        "root_cause_category": "MACHINE"
    })
    assert def_res.status_code == 201
    def_data = def_res.get_json()
    assert def_data["rework_quantity"] == 4
    assert def_data["scrap_quantity"] == 0

    # Create Containment Action on the defect
    cont_res = client.post("/api/defects/DEF-2026-000001/containment", json={
        "action_type": "LOT_QUARANTINE",
        "action_description": "Quarantine raw material lot and pause machining cell.",
        "quarantined_quantity": 500.0
    })
    assert cont_res.status_code == 201
    cont_data = cont_res.get_json()
    assert cont_data["status"] == "ACTIVE"

    # Verify Lot status is set to QUARANTINED
    lot_check = client.get("/api/material-lots/LOT-SUP-000001-2026-000001")
    assert lot_check.get_json()["status"] == "QUARANTINED"

