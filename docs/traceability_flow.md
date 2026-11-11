# Traceability Architecture & Anomaly Detection

## 1. Multi-Directional Traceability
The system supports bidirectional genealogy:

### 1.1 Backward Traceability (Defect Root Cause Investigation)
Starting with a shop-floor or field-reported non-conformance (`DEF-XXXXXX`), the traceability engine reconstructs the entire upstream lineage:
```
Product (SKU)
  └── Production Order (WO)
       └── BOM (Component Requirements)
            └── Material Consumption
                 └── Material Lot (Pedigree Batch)
                      └── Supplier (Vendor)
                           └── Process Step
                                └── Machine Cell
                                     └── Inspection Result
                                          └── Defect Incident
                                               └── Containment Action (Quarantine)
                                                    └── Corrective Action (CAPA)
                                                         └── Verification Audit
```

### 1.2 Forward Traceability (Containment & Recall Blast Radius)
Starting from a quarantined supplier (`SUP-XXXXXX`) or compromised raw material lot (`LOT-XXXXXX`):
1. Identify all `material_consumptions` referencing the lot.
2. Identify all affected `production_orders`.
3. Locate all `inspection_results` and products packaged from those orders.
4. Auto-generate quarantine containment orders across all inventory locations.

---

## 2. Injected Anomaly Scenarios & Detection Engine

| Scenario | Injected Condition | Detection Mechanism | Validation Code |
|---|---|---|---|
| **Scenario 1** | Defect points to nonexistent material lot (`LOT-SUP-999999-...`) | Foreign key audit & traceability relationship check | `BROKEN_FOREIGN_KEY_LOT` |
| **Scenario 2** | Mandatory BOM component missing consumption in completed order | BOM reconciliation engine comparison | `BOM_MATERIAL_NOT_CONSUMED` |
| **Scenario 3** | Attempted CAPA closure without recorded formal verification | Finite state machine lifecycle validator | `CAPA_CLOSED_BEFORE_VERIFICATION` |
| **Scenario 4** | Defect quantity exceeds inspected units (e.g. 25 defects on 10 inspected) | Mathematical bounds integrity checker | `DEFECT_COUNT_EXCEEDS_INSPECTED_QUANTITY` |
| **Scenario 5** | Defect points to non-existent work order (`WO-2026-999999`) | Upstream graph traversal integrity checker | `TRACEABILITY_CHAIN_BROKEN` |

Ground-truth anomaly labels are preserved separately in `backend/exports/ground_truth.json` and `backend/exports/ground_truth.csv` without leaking into application decision logic.

