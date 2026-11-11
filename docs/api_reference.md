# REST API Reference Manual

The Manufacturing Defect Traceability System provides a comprehensive RESTful API for integration with shop-floor SCADA, MES, CMM inspection stations, and ERP software.

Base URL: `http://127.0.0.1:5000/api`

---

## 1. Master Data Endpoints

### `GET /api/products`
Returns paginated list of manufactured product SKUs.
- **Query Parameters:**
  - `page` (int, default: 1)
  - `per_page` (int, default: 50)
  - `search` (string, optional: SKU or name substring)
  - `category` (string, optional)
- **Response `200 OK`:**
```json
{
  "items": [
    {
      "id": "SKU-000001",
      "name": "Powertrain Components Model-B001",
      "category": "Powertrain Components",
      "unit_of_measure": "PCS",
      "target_cycle_time_mins": 25.4,
      "standard_cost": 184.20,
      "is_active": true,
      "bom_items_count": 3
    }
  ],
  "total": 200,
  "page": 1,
  "total_pages": 4
}
```

### `POST /api/products`
Creates a new product record.
- **Request Body:**
```json
{
  "id": "SKU-000201",
  "name": "High-Pressure Hydraulic Actuator",
  "category": "Precision Hydraulic Valves",
  "target_cycle_time_mins": 30.0,
  "standard_cost": 210.00
}
```
- **Response `201 Created`**

---

## 2. Traceability Endpoints

### `GET /api/traceability`
Executes multi-tier forward or backward genealogy lookup.
- **Query Parameters:**
  - `type` (`defect`, `product`, `order`, `lot`, `supplier`, `machine`)
  - `id` (e.g. `DEF-2026-000001`)
- **Response `200 OK` (when valid):**
```json
{
  "query_type": "defect",
  "query_id": "DEF-2026-000001",
  "status": "VALID",
  "broken_links": [],
  "nodes": {
    "product": { "id": "SKU-000005", "name": "Powertrain Components Model-F005" },
    "production_order": { "id": "WO-2026-000005", "status": "COMPLETED" },
    "material_lot": { "id": "LOT-SUP-000001-2026-000011", "status": "RELEASED" },
    "supplier": { "id": "SUP-000001", "name": "Apex Industrial", "code": "VEND-0001" },
    "machine": { "id": "MAC-005", "name": "Precision Lathe #05", "line": "Line-A" },
    "process_step": { "id": "STEP-005", "name": "Deburring & Ultrasonic Wash" },
    "inspection_result": { "id": "INSP-WO-2026-000050-006", "result": "FAIL" },
    "defect": {
      "id": "DEF-2026-000001",
      "defect_code": "DIM-001",
      "defect_type": "Dimensional Out-of-Tolerance",
      "severity": "MAJOR",
      "disposition": "SCRAP",
      "defect_quantity": 2
    },
    "containment_actions": [
      { "action_type": "LOT_QUARANTINE", "quarantined_quantity": 50.0, "status": "COMPLETED" }
    ],
    "corrective_actions": [
      { "id": "CAPA-2026-000001", "status": "VERIFIED", "verified_by": "QA Director Vance" }
    ],
    "verification_status": {
      "is_verified": true,
      "verified_by": "QA Director Vance"
    }
  }
}
```

- **Response `200 OK` (when broken relationship detected, e.g. Anomaly Scenario 1):**
```json
{
  "query_type": "defect",
  "query_id": "DEF-2026-001594",
  "status": "BROKEN_LINK",
  "broken_links": [
    {
      "from": "Defect",
      "to": "MaterialLot",
      "reference_id": "LOT-SUP-999999-2026-999999",
      "reason": "Referenced Material Lot 'LOT-SUP-999999-2026-999999' does not exist in master registry (Foreign Key Integrity Violation)."
    }
  ]
}
```

---

## 3. Corrective Action (CAPA) Lifecycle Endpoints

### `POST /api/capas/<capa_id>/verify`
Performs formal verification audit required before closure.
- **Request Body:**
```json
{
  "verified_by": "QA Director Vance",
  "verification_notes": "Tested 5 sample lots with 0 repeat non-conformances. Cpk confirmed > 1.67."
}
```
- **Response `200 OK`**

### `POST /api/capas/<capa_id>/close`
Closes a verified CAPA.
- **Business Rule 9 Check:** If the CAPA has NOT been verified, the endpoint rejects the closure:
```json
// Status: 400 Bad Request
{
  "code": "LIFECYCLE_VIOLATION",
  "error": "Cannot close Corrective Action CAPA-2026-001195: Formal verification must be completed before closure.",
  "status": "REJECTED_LIFECYCLE_VIOLATION"
}
```

---

## 4. Analytics & Quality KPIs

### `GET /api/analytics/dashboard`
Returns live KPI cards computed from MySQL tables.
```json
{
  "defect_rate": 0.49,
  "open_corrective_actions": 398,
  "rework_quantity": 1382,
  "scrap_quantity": 1283,
  "total_defective_units": 4002,
  "total_defects": 1594,
  "total_inspected_units": 818990,
  "total_inspections": 20000,
  "total_material_lots": 2000,
  "total_production_orders": 5000,
  "total_products": 200,
  "total_suppliers": 50
}
```
