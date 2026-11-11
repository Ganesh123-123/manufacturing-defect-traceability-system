def setup_full_trace_chain(client):
    client.post("/api/products", json={"id": "SKU-000001", "name": "Precision Sensor Head", "category": "Sensors"})
    client.post("/api/boms", json={
        "parent_product_id": "SKU-000001",
        "component_sku": "MAT-OPTICAL-LENS",
        "component_name": "Optical Sapphire Glass",
        "quantity_per_unit": 1.0
    })
    client.post("/api/suppliers", json={"id": "SUP-000001", "name": "Optics Global", "code": "SUP-OPTIC"})
    client.post("/api/material-lots", json={
        "id": "LOT-SUP-000001-2026-000001",
        "supplier_id": "SUP-000001",
        "material_sku": "MAT-OPTICAL-LENS",
        "material_name": "Optical Sapphire Glass",
        "initial_quantity": 500.0
    })
    client.post("/api/machines", json={
        "id": "MAC-001",
        "machine_code": "MAC-001",
        "name": "Precision Lens Mount Robot",
        "type": "Robotics",
        "line": "Line-A"
    })
    client.post("/api/process-steps", json={
        "id": "STEP-010",
        "step_code": "STEP-010",
        "name": "Optic Alignment",
        "sequence_number": 10
    })
    client.post("/api/production-orders", json={
        "id": "WO-2026-000001",
        "product_id": "SKU-000001",
        "target_quantity": 20
    })
    client.post("/api/material-consumptions", json={
        "production_order_id": "WO-2026-000001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "consumed_quantity": 20.0
    })
    client.post("/api/inspection-plans", json={
        "id": "IP-SKU-000001-01",
        "product_id": "SKU-000001",
        "name": "Optic Alignment Check"
    })
    client.post("/api/inspections", json={
        "id": "INSP-WO-2026-000001-001",
        "inspection_plan_id": "IP-SKU-000001-01",
        "production_order_id": "WO-2026-000001",
        "machine_id": "MAC-001",
        "step_id": "STEP-010",
        "inspected_quantity": 20,
        "passed_quantity": 19,
        "failed_quantity": 1,
        "result": "FAIL"
    })
    client.post("/api/defects", json={
        "id": "DEF-2026-000001",
        "inspection_result_id": "INSP-WO-2026-000001-001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "machine_id": "MAC-001",
        "step_id": "STEP-010",
        "defect_code": "OPT-001",
        "defect_type": "Optical Aberration",
        "severity": "MAJOR",
        "defect_quantity": 1,
        "disposition": "REWORK"
    })
    client.post("/api/defects/DEF-2026-000001/containment", json={
        "action_type": "LOT_QUARANTINE",
        "action_description": "Quarantine lens lot",
        "quarantined_quantity": 50.0
    })
    client.post("/api/capas", json={
        "id": "CAPA-2026-000001",
        "defect_id": "DEF-2026-000001",
        "title": "Recalibrate Optical Sensor Jig"
    })

def test_full_traceability_chain(client):
    setup_full_trace_chain(client)

    # Search traceability by defect
    res = client.get("/api/traceability?type=defect&id=DEF-2026-000001")
    assert res.status_code == 200
    chain = res.get_json()

    assert chain["status"] == "VALID"
    nodes = chain["nodes"]

    # Verify every required link in prompt Section 10
    assert nodes["defect"]["id"] == "DEF-2026-000001"
    assert nodes["inspection_result"]["id"] == "INSP-WO-2026-000001-001"
    assert nodes["production_order"]["id"] == "WO-2026-000001"
    assert nodes["product"]["id"] == "SKU-000001"
    assert len(nodes["boms"]) >= 1
    assert len(nodes["material_consumptions"]) >= 1
    assert nodes["material_lot"]["id"] == "LOT-SUP-000001-2026-000001"
    assert nodes["supplier"]["id"] == "SUP-000001"
    assert nodes["machine"]["id"] == "MAC-001"
    assert nodes["process_step"]["id"] == "STEP-010"
    assert len(nodes["containment_actions"]) >= 1
    assert len(nodes["corrective_actions"]) >= 1
    assert "verification_status" in nodes

def test_traceability_by_other_entities(client):
    setup_full_trace_chain(client)

    # Trace by Product
    p_res = client.get("/api/traceability?type=product&id=SKU-000001")
    assert p_res.status_code == 200
    assert p_res.get_json()["product"]["id"] == "SKU-000001"

    # Trace by Supplier
    s_res = client.get("/api/traceability?type=supplier&id=SUP-000001")
    assert s_res.status_code == 200
    assert s_res.get_json()["supplier"]["id"] == "SUP-000001"

    # Trace by Lot
    l_res = client.get("/api/traceability?type=lot&id=LOT-SUP-000001-2026-000001")
    assert l_res.status_code == 200
    assert l_res.get_json()["lot"]["id"] == "LOT-SUP-000001-2026-000001"

    # Trace machine inspection and defect history
    m_res = client.get("/api/traceability?type=machine&id=MAC-001")
    assert m_res.status_code == 200
    machine_history = m_res.get_json()
    assert machine_history["machine"]["id"] == "MAC-001"
    assert machine_history["inspections_count"] == 1
    assert machine_history["inspections"][0]["id"] == "INSP-WO-2026-000001-001"
    assert machine_history["defects_count"] == 1
    assert machine_history["defects"][0]["id"] == "DEF-2026-000001"

    # Non-existent query should 404
    fail_res = client.get("/api/traceability?type=defect&id=DEF-NONEXISTENT")
    assert fail_res.status_code == 404
