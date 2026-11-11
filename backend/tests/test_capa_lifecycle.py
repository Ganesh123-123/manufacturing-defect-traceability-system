def setup_defect(client):
    client.post("/api/products", json={"id": "SKU-000001", "name": "Precision Housing", "category": "Mechanical"})
    client.post("/api/suppliers", json={"id": "SUP-000001", "name": "Foundry Inc", "code": "SUP-FND"})
    client.post("/api/material-lots", json={
        "id": "LOT-SUP-000001-2026-000001",
        "supplier_id": "SUP-000001",
        "material_sku": "MAT-HOUSING-CASTING",
        "material_name": "Aluminum Casting",
        "initial_quantity": 1000.0
    })
    client.post("/api/production-orders", json={
        "id": "WO-2026-000001",
        "product_id": "SKU-000001",
        "target_quantity": 50
    })
    client.post("/api/inspection-plans", json={
        "id": "IP-SKU-000001-01",
        "product_id": "SKU-000001",
        "name": "Dimensional Check"
    })
    client.post("/api/inspections", json={
        "id": "INSP-WO-2026-000001-001",
        "inspection_plan_id": "IP-SKU-000001-01",
        "production_order_id": "WO-2026-000001",
        "inspected_quantity": 20,
        "passed_quantity": 18,
        "failed_quantity": 2,
        "result": "FAIL"
    })
    client.post("/api/defects", json={
        "id": "DEF-2026-000001",
        "inspection_result_id": "INSP-WO-2026-000001-001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "defect_code": "CRK-003",
        "defect_type": "Micro-crack",
        "severity": "CRITICAL",
        "defect_quantity": 2,
        "disposition": "SCRAP"
    })

def test_capa_verification_and_closure_workflow(client):
    setup_defect(client)

    # 1. Create CAPA
    capa_res = client.post("/api/capas", json={
        "id": "CAPA-2026-000001",
        "defect_id": "DEF-2026-000001",
        "title": "Resolve Casting Porosity and Micro-Cracks",
        "assigned_to": "Senior Quality Specialist"
    })
    assert capa_res.status_code == 201
    capa_data = capa_res.get_json()
    assert capa_data["status"] == "OPEN"

    # 2. Rule 9: Attempting to close UNVERIFIED CAPA must be rejected!
    premature_close = client.post("/api/capas/CAPA-2026-000001/close", json={
        "closed_by": "Plant Manager",
        "notes": "Attempt premature closure without verification"
    })
    assert premature_close.status_code == 400
    err_body = premature_close.get_json()
    assert "verification" in err_body["error"].lower()
    assert err_body.get("status") == "REJECTED_LIFECYCLE_VIOLATION"

    # Verify event recorded for rejected closure
    capa_check = client.get("/api/capas/CAPA-2026-000001")
    events = capa_check.get_json()["events"]
    rejections = [e for e in events if e["event_type"] == "REJECTED_CLOSURE"]
    assert len(rejections) == 1

    # 3. Perform formal verification
    verify_res = client.post("/api/capas/CAPA-2026-000001/verify", json={
        "verified_by": "QA Director Vance",
        "verification_notes": "Tested 3 sample lots with 0 defects."
    })
    assert verify_res.status_code == 200
    assert verify_res.get_json()["status"] == "VERIFIED"

    # 4. Now close verified CAPA (must succeed)
    close_res = client.post("/api/capas/CAPA-2026-000001/close", json={
        "closed_by": "QA Director Vance",
        "notes": "Closure approved and verified."
    })
    assert close_res.status_code == 200
    assert close_res.get_json()["status"] == "CLOSED"
