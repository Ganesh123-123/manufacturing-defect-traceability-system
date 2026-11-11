def test_analytics_endpoints(client):
    # Setup test data
    client.post("/api/products", json={"id": "SKU-000001", "name": "Valve A", "category": "Hydraulics"})
    client.post("/api/suppliers", json={"id": "SUP-000001", "name": "Foundry", "code": "SUP-FND"})
    client.post("/api/material-lots", json={
        "id": "LOT-SUP-000001-2026-000001",
        "supplier_id": "SUP-000001",
        "material_sku": "MAT-01",
        "material_name": "Ingot",
        "initial_quantity": 1000.0
    })
    client.post("/api/machines", json={
        "id": "MAC-001",
        "machine_code": "MAC-001",
        "name": "Lathe 1",
        "type": "CNC",
        "line": "Line-A"
    })
    client.post("/api/production-orders", json={
        "id": "WO-2026-000001",
        "product_id": "SKU-000001",
        "target_quantity": 100
    })
    client.post("/api/inspection-plans", json={
        "id": "IP-SKU-000001-01",
        "product_id": "SKU-000001",
        "name": "QC Plan"
    })
    client.post("/api/inspections", json={
        "id": "INSP-WO-2026-000001-001",
        "inspection_plan_id": "IP-SKU-000001-01",
        "production_order_id": "WO-2026-000001",
        "machine_id": "MAC-001",
        "inspected_quantity": 100,
        "passed_quantity": 90,
        "failed_quantity": 10,
        "result": "FAIL"
    })
    client.post("/api/defects", json={
        "id": "DEF-2026-000001",
        "inspection_result_id": "INSP-WO-2026-000001-001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "machine_id": "MAC-001",
        "defect_code": "DIM-001",
        "defect_type": "Variance",
        "severity": "MAJOR",
        "defect_quantity": 10,
        "disposition": "REWORK"
    })

    # Test Dashboard KPI
    kpi_res = client.get("/api/analytics/dashboard")
    assert kpi_res.status_code == 200
    kpis = kpi_res.get_json()
    assert kpis["total_products"] == 1
    assert kpis["total_suppliers"] == 1
    assert kpis["total_inspections"] == 1
    assert kpis["total_defects"] == 1
    # Defect rate: 10 / 100 * 100 = 10.0%
    assert kpis["defect_rate"] == 10.0
    assert kpis["rework_quantity"] == 10

    # Test Analytics sub-endpoints
    sup_res = client.get("/api/analytics/suppliers")
    assert sup_res.status_code == 200
    assert len(sup_res.get_json()) >= 1

    mac_res = client.get("/api/analytics/machines")
    assert mac_res.status_code == 200
    assert len(mac_res.get_json()) >= 1

    prod_res = client.get("/api/analytics/products")
    assert prod_res.status_code == 200
    assert len(prod_res.get_json()) >= 1

    rws_res = client.get("/api/analytics/rework-vs-scrap")
    assert rws_res.status_code == 200
    assert rws_res.get_json()["rework"] == 10

    pf_res = client.get("/api/analytics/pass-fail")
    assert pf_res.status_code == 200
    assert pf_res.get_json()["passed_quantity"] == 90
    assert pf_res.get_json()["failed_quantity"] == 10

def test_system_audit_endpoints(client):
    # Test health
    h_res = client.get("/api/system/health")
    assert h_res.status_code == 200
    assert h_res.get_json()["status"] in ("healthy", "degraded")

    # Test validation
    v_res = client.get("/api/system/validate")
    assert v_res.status_code == 200
    val_data = v_res.get_json()
    assert "total_records" in val_data
    assert "total_checks" in val_data
    assert "validation_status" in val_data

    # Test anomaly scenarios metadata
    anom_res = client.get("/api/system/anomaly-scenarios")
    assert anom_res.status_code == 200
    scenarios = anom_res.get_json()
    assert len(scenarios) == 5

