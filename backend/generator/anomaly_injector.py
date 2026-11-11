import os
import csv
import json
import copy

class AnomalyInjector:
    def __init__(self):
        self.ground_truth = []

    def inject_anomalies(self, dataset):
        """
        Controlled anomaly injection step on baseline data.
        Modifies specifically designated anomaly records and records
        ground truth labels separately.
        """
        # Ensure deep copy so baseline isn't mutated in place unexpectedly
        data = dataset

        # -------------------------------------------------------------
        # Scenario 1: Defect links to nonexistent material lot
        # -------------------------------------------------------------
        if data["defects"]:
            target_defect = data["defects"][-1]
            nonexistent_lot = "LOT-SUP-999999-2026-999999"
            target_defect["material_lot_id"] = nonexistent_lot
            self.ground_truth.append({
                "anomaly_id": "SCENARIO_1",
                "issue_type": "BROKEN_FOREIGN_KEY_LOT",
                "affected_entity": "Defect",
                "affected_record_id": target_defect["id"],
                "expected_decision": "DETECT_BROKEN_FOREIGN_KEY_OR_TRACEABILITY_REFERENCE",
                "severity": "CRITICAL",
                "description": f"Defect {target_defect['id']} points to nonexistent material lot {nonexistent_lot}"
            })

        # -------------------------------------------------------------
        # Scenario 2: BOM material is not consumed
        # -------------------------------------------------------------
        # Find a completed production order and delete consumption of one mandatory BOM component
        completed_orders = [o for o in data["production_orders"] if o["status"] == "COMPLETED"]
        if completed_orders and data["material_consumptions"]:
            target_order = completed_orders[0]
            # Find consumptions for this order
            order_consumptions = [c for c in data["material_consumptions"] if c["production_order_id"] == target_order["id"]]
            if order_consumptions:
                removed_consumption = order_consumptions[0]
                data["material_consumptions"].remove(removed_consumption)
                self.ground_truth.append({
                    "anomaly_id": "SCENARIO_2",
                    "issue_type": "BOM_MATERIAL_NOT_CONSUMED",
                    "affected_entity": "ProductionOrder",
                    "affected_record_id": target_order["id"],
                    "expected_decision": "GENERATE_MATERIAL_CONSUMPTION_EXCEPTION",
                    "severity": "HIGH",
                    "description": f"Completed order {target_order['id']} is missing consumed BOM component {removed_consumption.get('bom_id')}"
                })

        # -------------------------------------------------------------
        # Scenario 3: Corrective action closes before verification
        # -------------------------------------------------------------
        if data["corrective_actions"]:
            # Pick a CAPA and set status='CLOSED' while stripping verification_date and verified_by
            target_capa = data["corrective_actions"][-1]
            target_capa["status"] = "CLOSED"
            target_capa["verification_date"] = None
            target_capa["verified_by"] = None
            target_capa["verification_notes"] = None
            self.ground_truth.append({
                "anomaly_id": "SCENARIO_3",
                "issue_type": "CAPA_CLOSED_BEFORE_VERIFICATION",
                "affected_entity": "CorrectiveAction",
                "affected_record_id": target_capa["id"],
                "expected_decision": "REJECT_CLOSURE_AND_RECORD_LIFECYCLE_VIOLATION",
                "severity": "MAJOR",
                "description": f"CAPA {target_capa['id']} transitioned to CLOSED without mandatory verification"
            })

        # -------------------------------------------------------------
        # Scenario 4: Defect count exceeds inspected quantity
        # -------------------------------------------------------------
        if data["inspections"] and data["defects"]:
            # Pick an inspection and matching defect; force defect quantity to exceed inspected quantity
            target_insp = data["inspections"][-1]
            # Find a defect linked or create a mismatch
            matching_defects = [d for d in data["defects"] if d["inspection_result_id"] == target_insp["id"]]
            if matching_defects:
                target_def = matching_defects[0]
            else:
                target_def = data["defects"][0]
                target_def["inspection_result_id"] = target_insp["id"]
            
            target_insp["inspected_quantity"] = 10
            target_def["defect_quantity"] = 25  # Exceeds inspected quantity 10
            self.ground_truth.append({
                "anomaly_id": "SCENARIO_4",
                "issue_type": "DEFECT_COUNT_EXCEEDS_INSPECTED_QUANTITY",
                "affected_entity": "Defect",
                "affected_record_id": target_def["id"],
                "expected_decision": "REJECT_INVALID_INSPECTION_OR_DEFECT_QUANTITY",
                "severity": "CRITICAL",
                "description": f"Defect quantity (25) exceeds inspected quantity (10) on inspection {target_insp['id']}"
            })

        # -------------------------------------------------------------
        # Scenario 5: Traceability chain breaks
        # -------------------------------------------------------------
        if len(data["defects"]) > 1:
            target_defect_5 = data["defects"][-2]
            target_defect_5["production_order_id"] = "WO-2026-999999"  # Non-existent order
            self.ground_truth.append({
                "anomaly_id": "SCENARIO_5",
                "issue_type": "TRACEABILITY_CHAIN_BROKEN",
                "affected_entity": "Defect",
                "affected_record_id": target_defect_5["id"],
                "expected_decision": "IDENTIFY_MISSING_UPSTREAM_OR_DOWNSTREAM_RELATIONSHIP",
                "severity": "CRITICAL",
                "description": f"Defect {target_defect_5['id']} references non-existent production order WO-2026-999999"
            })

        return data, self.ground_truth

    def export_ground_truth(self, export_dir):
        os.makedirs(export_dir, exist_ok=True)
        # JSON
        json_path = os.path.join(export_dir, "ground_truth.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.ground_truth, f, indent=2)

        # CSV
        csv_path = os.path.join(export_dir, "ground_truth.csv")
        fieldnames = ["anomaly_id", "issue_type", "affected_entity", "affected_record_id", "expected_decision", "severity", "description"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.ground_truth:
                writer.writerow(row)
        
        return json_path, csv_path

