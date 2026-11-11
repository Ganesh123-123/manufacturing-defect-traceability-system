def test_product_creation_and_retrieval(client):
    # Test valid product creation
    res = client.post("/api/products", json={
        "id": "SKU-000001",
        "name": "Precision Hydraulic Valve Assembly",
        "category": "Powertrain Components",
        "unit_of_measure": "PCS",
        "target_cycle_time_mins": 14.5,
        "standard_cost": 125.50
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] == "SKU-000001"
    assert data["name"] == "Precision Hydraulic Valve Assembly"

    # Test duplicate product ID rejection
    dup_res = client.post("/api/products", json={
        "id": "SKU-000001",
        "name": "Duplicate Item",
        "category": "Powertrain Components"
    })
    assert dup_res.status_code == 400

    # Test get product by ID
    get_res = client.get("/api/products/SKU-000001")
    assert get_res.status_code == 200
    assert get_res.get_json()["category"] == "Powertrain Components"

def test_supplier_creation_and_duplicate_code(client):
    # Test supplier creation
    res = client.post("/api/suppliers", json={
        "id": "SUP-000001",
        "name": "Apex Precision Casting Corp",
        "code": "VEND-0001",
        "contact_email": "qa@apexcasting.com",
        "contact_phone": "+1-555-019-2834",
        "country": "USA",
        "rating": 4.8
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] == "SUP-000001"
    assert data["code"] == "VEND-0001"

    # Duplicate code rejection
    dup_res = client.post("/api/suppliers", json={
        "id": "SUP-000002",
        "name": "Another Corp",
        "code": "VEND-0001"
    })
    assert dup_res.status_code == 400

def test_bom_creation_and_validation(client):
    # Setup product first
    client.post("/api/products", json={
        "id": "SKU-000002",
        "name": "Electronic Control Module",
        "category": "ECU"
    })

    # Add BOM item
    res = client.post("/api/boms", json={
        "parent_product_id": "SKU-000002",
        "component_sku": "MAT-MICROCONTROLLER-0001",
        "component_name": "32-Bit Dual Core MCU",
        "quantity_per_unit": 1.0,
        "unit_of_measure": "PCS",
        "scrap_factor": 0.02
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["component_sku"] == "MAT-MICROCONTROLLER-0001"
    assert data["quantity_per_unit"] == 1.0

    # BOM for non-existent product should fail
    fail_res = client.post("/api/boms", json={
        "parent_product_id": "SKU-999999",
        "component_sku": "MAT-RESISTOR",
        "component_name": "10k Resistor",
        "quantity_per_unit": 5.0
    })
    assert fail_res.status_code == 400
