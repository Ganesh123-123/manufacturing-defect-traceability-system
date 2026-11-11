import random
from datetime import datetime, timedelta
from faker import Faker
from backend.models import (
    Product, Supplier, MaterialLot, ProductionOrder, BOM, Machine,
    ProcessStep, ProcessStepMachine, InspectionPlan, InspectionResult,
    Defect, ContainmentAction, CorrectiveAction, MaterialConsumption,
    ProductionOrderMaterial, ProductionEvent, DefectEvent, CorrectiveActionEvent
)

PRODUCT_CATEGORIES = [
    "Powertrain Components",
    "Electronic Control Units",
    "Precision Hydraulic Valves",
    "Chassis Structural Castings",
    "Optical Sensor Housings",
    "Thermal Heat Exchangers",
    "Aerospace Fasteners",
    "Electric Drive Rotors"
]

COMPONENT_TEMPLATES = [
    ("Raw Forged Alloy Ingot", "KG", 1.25),
    ("Billet Aluminum Stock", "KG", 2.10),
    ("Microcontroller SMD Package", "PCS", 1.0),
    ("Multi-layer PCB Substrate", "PCS", 1.0),
    ("High-Temp Nitrile O-Ring", "PCS", 4.0),
    ("Precision CNC Valve Spool", "PCS", 1.0),
    ("M6 Titanium Hex Bolt", "PCS", 8.0),
    ("Epoxy Potting Resin", "LITER", 0.15),
    ("Thermal Interface Pad", "PCS", 2.0),
    ("Die-cast Sensor Enclosure", "PCS", 1.0)
]

MACHINE_TYPES = [
    "5-Axis CNC Milling", "Precision Lathe", "Surface Grinder",
    "SMT Pick-and-Place", "Wave Soldering Station", "Laser Welding Cell",
    "Die Casting Press", "Coordinate Measuring Machine (CMM)", "Automated Optical Inspection (AOI)"
]

DEFECT_TAXONOMY = [
    ("DIM-001", "Dimensional Out-of-Tolerance", "MAJOR", "MACHINE", "Bore diameter exceeds specified limit by 0.04mm"),
    ("SUR-002", "Surface Scratch & Porosity", "MINOR", "METHOD", "Micro-voids detected on polished sealing surface"),
    ("CRK-003", "Micro-Fracture / Stress Crack", "CRITICAL", "MATERIAL", "Sub-surface fatigue crack detected via ultrasonic probe"),
    ("WLD-004", "Incomplete Weld Penetration", "CRITICAL", "METHOD", "Root pass penetration below standard threshold"),
    ("ELC-005", "Solder Joint Bridging / Void", "MAJOR", "MACHINE", "Excessive solder volume bridging adjacent IC leads"),
    ("CON-006", "Particulate Contamination", "MINOR", "ENVIRONMENT", "Metallic debris entrapped within fluid pathway"),
    ("THD-007", "Thread Pitch Distortion", "MAJOR", "MACHINE", "Cross-threaded or stripped internal M6 threads"),
    ("COA-008", "Coating Delamination", "MINOR", "METHOD", "Anodized layer peeling along sharp edge fillet")
]

class DataFactory:
    def __init__(self, seed=20261022):
        self.seed = seed
        self.rng = random.Random(seed)
        self.faker = Faker()
        Faker.seed(seed)

    def generate_all(self, scale="starter"):
        """
        Generates structured record dictionaries.
        Scale options:
        - starter: 20 products, 10 suppliers, 100 lots, 200 orders, 1,000 inspections
        - full: 200 products, 50 suppliers, 2,000 lots, 5,000 orders, 20,000 inspections
        """
        if scale == "full":
            num_products = 200
            num_suppliers = 50
            num_lots = 2000
            num_orders = 5000
            num_inspections = 20000
            num_machines = 25
            num_steps = 35
        else:
            num_products = 20
            num_suppliers = 10
            num_lots = 100
            num_orders = 200
            num_inspections = 1000
            num_machines = 20
            num_steps = 30

        base_date = datetime(2026, 1, 1, 8, 0, 0)

        # 1. Products
        products = []
        for i in range(1, num_products + 1):
            sku = f"SKU-{i:06d}"
            cat = PRODUCT_CATEGORIES[(i - 1) % len(PRODUCT_CATEGORIES)]
            name = f"{cat} Model-{chr(65 + (i % 26))}{i:03d}"
            products.append({
                "id": sku,
                "name": name,
                "category": cat,
                "unit_of_measure": "PCS",
                "target_cycle_time_mins": round(self.rng.uniform(10.0, 45.0), 1),
                "standard_cost": round(self.rng.uniform(45.0, 450.0), 2),
                "is_active": True,
                "created_at": base_date + timedelta(days=(i % 30))
            })

        # 2. BOMs (2-4 components per product)
        boms = []
        bom_id_seq = 1
        for p in products:
            num_comps = 2 + (self.rng.randint(0, 2))
            chosen_comps = self.rng.sample(COMPONENT_TEMPLATES, num_comps)
            for comp_name, uom, base_qty in chosen_comps:
                comp_sku = f"MAT-{comp_name.replace(' ', '-').upper()[:12]}-{bom_id_seq:04d}"
                boms.append({
                    "id": bom_id_seq,
                    "parent_product_id": p["id"],
                    "component_sku": comp_sku,
                    "component_name": comp_name,
                    "quantity_per_unit": base_qty,
                    "unit_of_measure": uom,
                    "scrap_factor": round(self.rng.uniform(0.01, 0.05), 3),
                    "revision": "1.0",
                    "effective_from": base_date,
                    "created_at": base_date
                })
                bom_id_seq += 1

        # 3. Suppliers
        suppliers = []
        for i in range(1, num_suppliers + 1):
            sup_id = f"SUP-{i:06d}"
            sup_code = f"VEND-{i:04d}"
            company = f"{self.faker.company().replace(',', '')} Industrial"
            suppliers.append({
                "id": sup_id,
                "code": sup_code,
                "name": company,
                "contact_email": f"quality@{sup_code.lower()}.example.com",
                "contact_phone": f"+1-555-{self.rng.randint(100, 999)}-{self.rng.randint(1000, 9999)}",
                "country": "USA" if i % 3 != 0 else ("Germany" if i % 2 == 0 else "Japan"),
                "rating": round(self.rng.uniform(3.8, 5.0), 2),
                "status": "ACTIVE" if i % 15 != 0 else "ON_PROBATION",
                "created_at": base_date - timedelta(days=90)
            })

        # 4. Material Lots
        lots = []
        for i in range(1, num_lots + 1):
            sup = suppliers[(i - 1) % len(suppliers)]
            sup_num = int(sup["id"].split("-")[1])
            lot_id = f"LOT-SUP-{sup_num:06d}-2026-{i:06d}"
            comp_idx = (i - 1) % len(COMPONENT_TEMPLATES)
            c_name, c_uom, _ = COMPONENT_TEMPLATES[comp_idx]
            c_sku = f"MAT-{c_name.replace(' ', '-').upper()[:12]}-{comp_idx+1:04d}"
            init_qty = float(self.rng.randint(2000, 10000))
            rcv_date = base_date + timedelta(days=int(i * 180 / num_lots))

            lots.append({
                "id": lot_id,
                "supplier_id": sup["id"],
                "material_sku": c_sku,
                "material_name": c_name,
                "batch_number": f"BATCH-{lot_id}",
                "initial_quantity": init_qty,
                "remaining_quantity": init_qty,  # will decrement during consumption
                "unit_of_measure": c_uom,
                "received_date": rcv_date,
                "expiry_date": rcv_date + timedelta(days=365),
                "certificate_of_analysis": f"COA-{lot_id}",
                "status": "RELEASED",
                "created_at": rcv_date
            })

        # 5. Machines
        machines = []
        for i in range(1, num_machines + 1):
            mac_id = f"MAC-{i:03d}"
            m_type = MACHINE_TYPES[(i - 1) % len(MACHINE_TYPES)]
            line = f"Line-{chr(65 + ((i - 1) % 4))}"
            machines.append({
                "id": mac_id,
                "machine_code": mac_id,
                "name": f"{m_type} #{i:02d}",
                "type": m_type,
                "line": line,
                "location": f"Bay-{((i - 1) % 5) + 1}",
                "status": "OPERATIONAL" if i % 12 != 0 else "MAINTENANCE",
                "calibration_due_date": base_date + timedelta(days=120),
                "created_at": base_date - timedelta(days=180)
            })

        # 6. Process Steps
        process_steps = []
        step_names = [
            "Raw Material Receipt & Assay", "Rough Machining", "Precision CNC Turning",
            "Milling & Pocketing", "Deburring & Ultrasonic Wash", "Thermal Heat Treatment",
            "Surface Anodizing & Passivation", "Micro-soldering & SMT Placement",
            "Sub-Assembly Insertion", "Automated Optical Inspection", "Torque & Fastener Assembly",
            "Leak Testing & Pressure Decay", "Laser Marking & Barcoding", "Functional Bench Test",
            "Final Cleanroom Packaging"
        ]
        for i in range(1, num_steps + 1):
            s_id = f"STEP-{i:03d}"
            s_name = step_names[(i - 1) % len(step_names)] + (f" Stage-{((i-1)//len(step_names))+1}" if i > len(step_names) else "")
            process_steps.append({
                "id": s_id,
                "step_code": s_id,
                "name": s_name,
                "sequence_number": i * 10,
                "standard_duration_mins": round(self.rng.uniform(8.0, 30.0), 1),
                "inspection_required": True if i % 2 == 0 else False,
                "description": f"Standard operating procedure for {s_name}",
                "created_at": base_date - timedelta(days=180)
            })

        # 7. Process Step Machines
        step_machines = []
        sm_id = 1
        for step in process_steps:
            m = machines[(sm_id - 1) % len(machines)]
            step_machines.append({
                "id": sm_id,
                "step_id": step["id"],
                "machine_id": m["id"],
                "is_primary": True,
                "setup_time_mins": 15.0,
                "created_at": base_date
            })
            sm_id += 1

        # 8. Inspection Plans (1 plan per product)
        inspection_plans = []
        for p in products:
            plan_id = f"IP-{p['id']}-01"
            inspection_plans.append({
                "id": plan_id,
                "product_id": p["id"],
                "step_id": process_steps[min(9, len(process_steps) - 1)]["id"],
                "name": f"Master Quality Plan for {p['name']}",
                "sampling_type": "AQL_NORMAL",
                "sample_size_percentage": 10.0,
                "tolerance_critical": 0.0,
                "tolerance_major": 1.0,
                "tolerance_minor": 2.5,
                "criteria": "Verify geometric dimensions, surface finish Ra <= 0.8um, zero crack tolerance.",
                "is_active": True,
                "created_at": base_date
            })

        # 9. Production Orders
        orders = []
        for i in range(1, num_orders + 1):
            wo_id = f"WO-2026-{i:06d}"
            prod = products[(i - 1) % len(products)]
            target_qty = self.rng.choice([50, 100, 200, 500])
            status = "COMPLETED" if i <= int(num_orders * 0.85) else ("IN_PROGRESS" if i <= int(num_orders * 0.95) else "PLANNED")
            start_date = base_date + timedelta(days=int(i * 240 / num_orders), hours=self.rng.randint(0, 12))
            end_date = start_date + timedelta(days=self.rng.randint(2, 5)) if status == "COMPLETED" else None

            orders.append({
                "id": wo_id,
                "product_id": prod["id"],
                "target_quantity": target_qty,
                "completed_quantity": target_qty if status == "COMPLETED" else (int(target_qty * 0.5) if status == "IN_PROGRESS" else 0),
                "scrapped_quantity": 0,
                "rework_quantity": 0,
                "status": status,
                "planned_start_date": start_date,
                "planned_end_date": start_date + timedelta(days=5),
                "actual_start_date": start_date if status != "PLANNED" else None,
                "actual_end_date": end_date,
                "batch_number": f"BATCH-{wo_id}",
                "created_at": start_date - timedelta(days=1)
            })

        # Pre-index BOMs by product
        boms_by_prod = {}
        for b in boms:
            boms_by_prod.setdefault(b["parent_product_id"], []).append(b)

        # 10. Material Consumptions (Reconciling with BOM requirements)
        consumptions = []
        c_id = 1
        lot_idx = 0
        for o in orders:
            if o["status"] in ("COMPLETED", "IN_PROGRESS"):
                prod_boms = boms_by_prod.get(o["product_id"], [])
                for b in prod_boms:
                    req_qty = b["quantity_per_unit"] * o["completed_quantity"]
                    if req_qty <= 0:
                        req_qty = b["quantity_per_unit"] * (o["target_quantity"] * 0.5)
                    # Assign a material lot
                    chosen_lot = lots[lot_idx % len(lots)]
                    lot_idx += 1
                    # Decrement remaining quantity
                    chosen_lot["remaining_quantity"] = max(0.0, chosen_lot["remaining_quantity"] - req_qty)
                    consumptions.append({
                        "id": c_id,
                        "production_order_id": o["id"],
                        "material_lot_id": chosen_lot["id"],
                        "bom_id": b["id"],
                        "consumed_quantity": round(req_qty, 2),
                        "unit_of_measure": b["unit_of_measure"],
                        "consumed_at": o["actual_start_date"] or base_date,
                        "created_at": o["actual_start_date"] or base_date
                    })
                    c_id += 1

        # 11. Production Events
        prod_events = []
        pe_id = 1
        for o in orders:
            prod_events.append({
                "id": pe_id,
                "production_order_id": o["id"],
                "step_id": process_steps[0]["id"],
                "machine_id": machines[0]["id"],
                "event_type": "CREATED",
                "status_from": None,
                "status_to": "PLANNED",
                "details": f"Work order {o['id']} scheduled for manufacturing.",
                "timestamp": o["created_at"]
            })
            pe_id += 1
            if o["status"] in ("IN_PROGRESS", "COMPLETED"):
                prod_events.append({
                    "id": pe_id,
                    "production_order_id": o["id"],
                    "step_id": process_steps[1]["id"],
                    "machine_id": machines[1 % len(machines)]["id"],
                    "event_type": "STARTED",
                    "status_from": "PLANNED",
                    "status_to": "IN_PROGRESS",
                    "details": "Production line setup complete and run initiated.",
                    "timestamp": o["actual_start_date"]
                })
                pe_id += 1
            if o["status"] == "COMPLETED":
                prod_events.append({
                    "id": pe_id,
                    "production_order_id": o["id"],
                    "step_id": process_steps[-1]["id"],
                    "machine_id": machines[-1]["id"],
                    "event_type": "COMPLETED",
                    "status_from": "IN_PROGRESS",
                    "status_to": "COMPLETED",
                    "details": f"Work order {o['id']} completed successfully.",
                    "timestamp": o["actual_end_date"]
                })
                pe_id += 1

        # 12. Inspections & Defects
        # We need num_inspections total.
        inspections = []
        defects = []
        capas = []
        containment_actions = []
        defect_events = []
        capa_events = []

        defect_id_seq = 1
        capa_id_seq = 1
        ca_id_seq = 1
        de_id_seq = 1
        ce_id_seq = 1

        orders_pool = [o for o in orders if o["status"] in ("COMPLETED", "IN_PROGRESS")]
        if not orders_pool:
            orders_pool = orders

        # Pre-index consumptions by order for fast lot lookup
        order_to_lots = {}
        for c in consumptions:
            order_to_lots.setdefault(c["production_order_id"], []).append(c["material_lot_id"])

        plans_by_prod = {ip["product_id"]: ip for ip in inspection_plans}

        for i in range(1, num_inspections + 1):
            o = orders_pool[(i - 1) % len(orders_pool)]
            wo_num = int(o["id"].split("-")[2])
            insp_seq = ((i - 1) // len(orders_pool)) + 1
            insp_id = f"INSP-WO-2026-{wo_num:06d}-{insp_seq:03d}"

            plan = plans_by_prod.get(o["product_id"], inspection_plans[0])
            m = machines[(i - 1) % len(machines)]
            step = process_steps[(i - 1) % len(process_steps)]

            inspected_qty = self.rng.choice([10, 20, 25, 50, 100])
            
            # Realistic defect occurrence (~8% probability)
            has_defect = (self.rng.random() < 0.08)
            failed_qty = self.rng.randint(1, min(4, inspected_qty)) if has_defect else 0
            passed_qty = inspected_qty - failed_qty
            result = "PASS" if failed_qty == 0 else "FAIL"

            insp_date = (o["actual_start_date"] or base_date) + timedelta(hours=self.rng.randint(1, 48))

            inspections.append({
                "id": insp_id,
                "inspection_plan_id": plan["id"],
                "production_order_id": o["id"],
                "step_id": step["id"],
                "machine_id": m["id"],
                "inspected_quantity": inspected_qty,
                "passed_quantity": passed_qty,
                "failed_quantity": failed_qty,
                "result": result,
                "inspected_at": insp_date,
                "inspector_name": f"QC-Tech #{((i - 1) % 12) + 1:02d}",
                "notes": f"Standard inspection checkpoint on {m['name']}." if result == "PASS" else "Non-conformance identified.",
                "created_at": insp_date
            })

            # If defect, record Defect and related actions
            if has_defect:
                def_id = f"DEF-2026-{defect_id_seq:06d}"
                d_tax = DEFECT_TAXONOMY[(defect_id_seq - 1) % len(DEFECT_TAXONOMY)]
                code, d_type, sev, root_cat, desc = d_tax

                disposition = self.rng.choice(["REWORK", "SCRAP", "USE_AS_IS"])
                rework_qty = failed_qty if disposition == "REWORK" else 0
                scrap_qty = failed_qty if disposition == "SCRAP" else 0

                # Trace to material lot consumed in this order
                avail_lots = order_to_lots.get(o["id"], [])
                linked_lot_id = self.rng.choice(avail_lots) if avail_lots else lots[(defect_id_seq - 1) % len(lots)]["id"]

                defects.append({
                    "id": def_id,
                    "inspection_result_id": insp_id,
                    "production_order_id": o["id"],
                    "material_lot_id": linked_lot_id,
                    "machine_id": m["id"],
                    "step_id": step["id"],
                    "defect_code": code,
                    "defect_type": d_type,
                    "severity": sev,
                    "defect_quantity": failed_qty,
                    "disposition": disposition,
                    "rework_quantity": rework_qty,
                    "scrap_quantity": scrap_qty,
                    "root_cause_category": root_cat,
                    "description": desc,
                    "status": "CAPA_INITIATED" if sev == "CRITICAL" else "IDENTIFIED",
                    "detected_at": insp_date,
                    "created_at": insp_date
                })

                # Defect Event
                defect_events.append({
                    "id": de_id_seq,
                    "defect_id": def_id,
                    "event_type": "CREATED",
                    "from_status": None,
                    "to_status": "IDENTIFIED",
                    "note": f"Defect logged with disposition {disposition} (Qty: {failed_qty})",
                    "timestamp": insp_date
                })
                de_id_seq += 1

                # Update order stats
                o["rework_quantity"] += rework_qty
                o["scrapped_quantity"] += scrap_qty

                # Containment Action for CRITICAL or MAJOR defects
                current_ca_id = None
                if sev in ("CRITICAL", "MAJOR"):
                    containment_actions.append({
                        "id": ca_id_seq,
                        "defect_id": def_id,
                        "action_type": "LOT_QUARANTINE",
                        "action_description": f"Immediate quarantine of lot {linked_lot_id} and halt run.",
                        "target_lot_id": linked_lot_id,
                        "quarantined_quantity": float(self.rng.randint(50, 500)),
                        "status": "COMPLETED",
                        "initiated_at": insp_date,
                        "completed_at": insp_date + timedelta(hours=4)
                    })
                    current_ca_id = ca_id_seq
                    ca_id_seq += 1

                # Corrective Action (CAPA) for critical/major defects (~40% of defects)
                if sev in ("CRITICAL", "MAJOR") or (defect_id_seq % 3 == 0):
                    capa_id = f"CAPA-2026-{capa_id_seq:06d}"
                    # Lifecycle states: OPEN, IN_PROGRESS, PENDING_VERIFICATION, VERIFIED, CLOSED
                    is_closed = (capa_id_seq % 2 == 0)
                    is_verified = is_closed or (capa_id_seq % 3 == 0)

                    v_date = insp_date + timedelta(days=7) if is_verified else None
                    v_by = "QA Director Vance" if is_verified else None
                    c_date = insp_date + timedelta(days=10) if is_closed else None
                    status = "CLOSED" if is_closed else ("VERIFIED" if is_verified else "IN_PROGRESS")

                    capas.append({
                        "id": capa_id,
                        "defect_id": def_id,
                        "containment_action_id": current_ca_id,
                        "title": f"CAPA: Resolve {d_type} on {m['name']}",
                        "description": f"Root cause investigation and corrective containment for {def_id}.",
                        "root_cause_analysis": f"Root cause traced to {root_cat.lower()} tolerance drift.",
                        "corrective_action_plan": "Recalibrated tooling offsets and replaced worn guide bearings.",
                        "preventive_action_plan": "Updated SPC control limits and daily operator checklist.",
                        "status": status,
                        "assigned_to": f"Engineer #{((capa_id_seq - 1) % 8) + 1}",
                        "target_date": insp_date + timedelta(days=14),
                        "verification_date": v_date,
                        "verified_by": v_by,
                        "verification_notes": "Post-mitigation 5-lot audit confirmed Cpk > 1.67." if is_verified else None,
                        "closure_date": c_date,
                        "created_at": insp_date
                    })

                    # CAPA Event
                    capa_events.append({
                        "id": ce_id_seq,
                        "capa_id": capa_id,
                        "event_type": "CREATED",
                        "from_status": None,
                        "to_status": "OPEN",
                        "changed_by": "QA Lead",
                        "note": f"CAPA logged for {def_id}",
                        "timestamp": insp_date
                    })
                    ce_id_seq += 1

                    if is_verified:
                        capa_events.append({
                            "id": ce_id_seq,
                            "capa_id": capa_id,
                            "event_type": "VERIFIED",
                            "from_status": "PENDING_VERIFICATION",
                            "to_status": "VERIFIED",
                            "changed_by": v_by,
                            "note": "Formal verification completed successfully.",
                            "timestamp": v_date
                        })
                        ce_id_seq += 1

                    if is_closed:
                        capa_events.append({
                            "id": ce_id_seq,
                            "capa_id": capa_id,
                            "event_type": "CLOSED",
                            "from_status": "VERIFIED",
                            "to_status": "CLOSED",
                            "changed_by": "QA Director Vance",
                            "note": "Final sign-off and closure complete.",
                            "timestamp": c_date
                        })
                        ce_id_seq += 1

                    capa_id_seq += 1

                defect_id_seq += 1

        return {
            "products": products,
            "boms": boms,
            "suppliers": suppliers,
            "material_lots": lots,
            "machines": machines,
            "process_steps": process_steps,
            "step_machines": step_machines,
            "inspection_plans": inspection_plans,
            "production_orders": orders,
            "material_consumptions": consumptions,
            "production_events": prod_events,
            "inspections": inspections,
            "defects": defects,
            "containment_actions": containment_actions,
            "corrective_actions": capas,
            "defect_events": defect_events,
            "capa_events": capa_events
        }
