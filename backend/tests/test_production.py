def test_material_lot_creation(client):
    # Setup supplier
    client.post("/api/suppliers", json={
        "id": "SUP-000001",
        "name": "Titanium Forgings Ltd",
        "code": "VEND-0001"
    })

    # Create Material Lot
    res = client.post("/api/material-lots", json={
        "id": "LOT-SUP-000001-2026-000001",
        "supplier_id": "SUP-000001",
        "material_sku": "MAT-TITANIUM-INGOT",
        "material_name": "Grade-5 Titanium Raw Billet",
        "batch_number": "BATCH-TITAN-01",
        "initial_quantity": 5000.0,
        "unit_of_measure": "KG"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] == "LOT-SUP-000001-2026-000001"
    assert data["remaining_quantity"] == 5000.0

    # Material lot with invalid supplier must fail
    fail_res = client.post("/api/material-lots", json={
        "id": "LOT-SUP-999999-2026-000001",
        "supplier_id": "SUP-999999",
        "material_sku": "MAT-FAIL",
        "material_name": "Test",
        "initial_quantity": 100.0
    })
    assert fail_res.status_code == 400

def test_production_order_and_consumption(client):
    # Setup Product and Supplier and Lot
    client.post("/api/products", json={"id": "SKU-000001", "name": "Titanium Bracket", "category": "Aerospace"})
    client.post("/api/suppliers", json={"id": "SUP-000001", "name": "Titan Supplier", "code": "SUP-TITAN"})
    client.post("/api/material-lots", json={
        "id": "LOT-SUP-000001-2026-000001",
        "supplier_id": "SUP-000001",
        "material_sku": "MAT-TITANIUM",
        "material_name": "Titanium Ingot",
        "initial_quantity": 1000.0
    })

    # Create Production Order
    wo_res = client.post("/api/production-orders", json={
        "id": "WO-2026-000001",
        "product_id": "SKU-000001",
        "target_quantity": 100
    })
    assert wo_res.status_code == 201
    wo_data = wo_res.get_json()
    assert wo_data["id"] == "WO-2026-000001"
    assert wo_data["status"] == "PLANNED"

    # Record Material Consumption
    cons_res = client.post("/api/material-consumptions", json={
        "production_order_id": "WO-2026-000001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "consumed_quantity": 250.0,
        "unit_of_measure": "KG"
    })
    assert cons_res.status_code == 201

    # Verify Lot Remaining Quantity decremented
    lot_res = client.get("/api/material-lots/LOT-SUP-000001-2026-000001")
    assert lot_res.status_code == 200
    assert lot_res.get_json()["remaining_quantity"] == 750.0

    # Over-consumption beyond remaining quantity should fail
    over_res = client.post("/api/material-consumptions", json={
        "production_order_id": "WO-2026-000001",
        "material_lot_id": "LOT-SUP-000001-2026-000001",
        "consumed_quantity": 1500.0
    })
    assert over_res.status_code == 400
