# Anomaly Scenarios & Validation Engine Guide

This document details the 5 controlled manufacturing anomaly scenarios injected into the test dataset, explaining their industrial context, technical detection mechanism, and verification steps.

---

## Scenario 1: Defect Links to Nonexistent Material Lot
- **Industrial Context:** An operator reports a non-conformance and manually transcribes a heat lot number from a damaged paper tag that was mistyped or does not exist in the warehouse ERP registry.
- **Injected Anomaly:** `DEF-2026-001594` references lot `LOT-SUP-999999-2026-999999`.
- **System Detection:**
  - Database Audit: Detects broken foreign key constraint.
  - Traceability Engine: Returns `status: BROKEN_LINK` with detailed message:
    `Referenced Material Lot 'LOT-SUP-999999-2026-999999' does not exist in master registry.`
  - UI Visualizer: Flags the Material Lot node in red with warning icon.

---

## Scenario 2: BOM Material Is Not Consumed
- **Industrial Context:** A production work order is marked as `COMPLETED`, but assembly traveler logs show that a critical component (e.g. O-ring or potting resin) was never logged as consumed. This indicates an unauthorized bypass of assembly steps or missed BOM reconciliation.
- **Injected Anomaly:** Work order `WO-2026-000001` has active BOM components where consumption was zero.
- **System Detection:**
  - Automated Audit: Compares `production_order_materials` vs. `material_consumptions`.
  - Detection Flag: `BOM_MATERIAL_NOT_CONSUMED` with severity `HIGH`.

---

## Scenario 3: Corrective Action Closes Before Verification
- **Industrial Context:** To meet quarterly closure KPIs, an engineering lead attempts to mark an open CAPA as "Closed" before conducting a 30-day statistical capability study (Cpk > 1.67) or obtaining formal QA sign-off.
- **Injected Anomaly:** `CAPA-2026-001195` marked as `CLOSED` without `verification_date` or `verified_by`.
- **System Detection:**
  - Runtime API: `POST /api/capas/<id>/close` raises `LifecycleViolationException` (HTTP 400).
  - Event History: Automatically logs a `REJECTED_CLOSURE` event in `corrective_action_events` table preserving audit history.
  - Audit Engine: Catches unverified closure in `validation_summary.json`.

---

## Scenario 4: Defect Count Exceeds Inspected Quantity
- **Industrial Context:** A data entry error occurs at an automated optical inspection (AOI) station where an inspector enters 25 defects for a sample size of only 10 units.
- **Injected Anomaly:** Defect `DEF-2026-000001` has `defect_quantity = 25` on an inspection record with `inspected_quantity = 10`.
- **System Detection:**
  - Business Rule: `validate_defect_quantity` validates `defect_qty <= inspected_qty`.
  - Runtime API: Rejects invalid creation with `QuantityValidationException`.
  - Audit Engine: Flags `DEFECT_COUNT_EXCEEDS_INSPECTED_QUANTITY` with severity `CRITICAL`.

---

## Scenario 5: Traceability Chain Breaks
- **Industrial Context:** A quality defect record becomes orphaned due to data corruption, missing upstream work order reference, or deleted order travelers.
- **Injected Anomaly:** Defect `DEF-2026-001593` references non-existent work order `WO-2026-999999`.
- **System Detection:**
  - Traceability Engine: Discovers disconnected upstream node and returns:
    `Production order WO-2026-999999 is missing or broken.`
  - UI Visualizer: Renders node in highlighted red warning state.

---

## How to Test Anomalies in the UI

1. Open **[http://localhost:8000/#traceability](http://localhost:8000/#traceability)**.
2. In the **Quick Sample Queries** toolbar at the top:
   - Click **`Scenario 1 (Broken Lot)`** &rarr; Inspect the red-flagged Material Lot node and diagnostic banner.
   - Click **`Scenario 5 (Broken WO)`** &rarr; Inspect the missing work order warning.
3. Open **[http://localhost:8000/#reports](http://localhost:8000/#reports)** to view the live **Ground Truth Anomaly Log** and **Automated Quality & Integrity Validation Audit** table.

