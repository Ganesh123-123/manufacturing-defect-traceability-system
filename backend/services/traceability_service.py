from backend.database.connection import db
from backend.models import (
    Defect, InspectionResult, ProductionOrder, Product, MaterialLot,
    Supplier, Machine, ProcessStep, BOM, MaterialConsumption,
    ContainmentAction, CorrectiveAction
)
from backend.validation.exceptions import ValidationError

class TraceabilityService:
    @staticmethod
    def trace(query_type, query_id):
        """
        Unified traceability query by:
        - defect: Defect ID (e.g. DEF-2026-000001)
        - product: Product SKU (e.g. SKU-000001)
        - order: Production Order ID (e.g. WO-2026-000001)
        - lot: Material Lot ID (e.g. LOT-SUP-000001-2026-000001)
        - supplier: Supplier ID (e.g. SUP-000001)
        - machine: Machine ID (e.g. MAC-001)
        """
        query_type = query_type.lower()
        if query_type == "defect":
            return TraceabilityService.trace_defect(query_id)
        elif query_type in ("product", "sku"):
            return TraceabilityService.trace_product(query_id)
        elif query_type in ("order", "production_order", "wo"):
            return TraceabilityService.trace_production_order(query_id)
        elif query_type in ("lot", "material_lot"):
            return TraceabilityService.trace_material_lot(query_id)
        elif query_type == "supplier":
            return TraceabilityService.trace_supplier(query_id)
        elif query_type == "machine":
            return TraceabilityService.trace_machine(query_id)
        else:
            raise ValidationError(f"Unknown query_type: {query_type}. Allowed: defect, product, order, lot, supplier, machine.")

    @staticmethod
    def trace_defect(defect_id):
        defect = db.session.get(Defect, defect_id)
        if not defect:
            raise ValidationError(f"Defect '{defect_id}' not found in traceability index.", code="NOT_FOUND")

        chain = {
            "query_type": "defect",
            "query_id": defect_id,
            "status": "VALID",
            "broken_links": [],
            "nodes": {},
            "timeline": []
        }

        # 1. Defect Node
        chain["nodes"]["defect"] = defect.to_dict()

        # 2. Inspection Result
        insp = defect.inspection_result
        if insp:
            chain["nodes"]["inspection_result"] = insp.to_dict()
        else:
            chain["status"] = "BROKEN_LINK"
            chain["broken_links"].append({
                "from": "Defect",
                "to": "InspectionResult",
                "reference_id": defect.inspection_result_id,
                "reason": f"Referenced inspection {defect.inspection_result_id} does not exist."
            })

        # 3. Production Order
        order = db.session.get(ProductionOrder, defect.production_order_id)
        if order:
            chain["nodes"]["production_order"] = order.to_dict()
        else:
            chain["status"] = "BROKEN_LINK"
            chain["broken_links"].append({
                "from": "Defect",
                "to": "ProductionOrder",
                "reference_id": defect.production_order_id,
                "reason": f"Production order {defect.production_order_id} is missing or broken."
            })
            # fallback to inspection's production order if inspection exists
            if insp and insp.production_order:
                order = insp.production_order

        # 4. Product
        product = order.product if order else None
        if product:
            chain["nodes"]["product"] = product.to_dict()
        elif order:
            chain["status"] = "BROKEN_LINK"
            chain["broken_links"].append({
                "from": "ProductionOrder",
                "to": "Product",
                "reference_id": order.product_id,
                "reason": f"Product {order.product_id} is missing."
            })

        # 5. BOM
        boms = product.boms if product else []
        chain["nodes"]["boms"] = [b.to_dict() for b in boms]

        # 6. Material Consumption & Lots
        consumptions = order.consumptions if order else []
        chain["nodes"]["material_consumptions"] = [c.to_dict() for c in consumptions]

        # 7. Material Lot (Primary linked to defect or consumptions)
        lot = defect.material_lot
        if lot:
            chain["nodes"]["material_lot"] = lot.to_dict()
        elif defect.material_lot_id:
            chain["status"] = "BROKEN_LINK"
            chain["broken_links"].append({
                "from": "Defect",
                "to": "MaterialLot",
                "reference_id": defect.material_lot_id,
                "reason": f"Referenced Material Lot '{defect.material_lot_id}' does not exist in master registry (Foreign Key Integrity Violation)."
            })
        elif consumptions:
            # Fall back to lots consumed in this order
            first_lot = consumptions[0].material_lot
            if first_lot:
                chain["nodes"]["material_lot"] = first_lot.to_dict()
                chain["nodes"]["material_lot"]["note"] = "Inferred from production material consumption."

        # 8. Supplier
        supplier = None
        if lot and lot.supplier:
            supplier = lot.supplier
            chain["nodes"]["supplier"] = supplier.to_dict()
        elif lot and lot.supplier_id:
            chain["status"] = "BROKEN_LINK"
            chain["broken_links"].append({
                "from": "MaterialLot",
                "to": "Supplier",
                "reference_id": lot.supplier_id,
                "reason": f"Supplier {lot.supplier_id} not found."
            })

        # 9. Machine
        machine = defect.machine or (insp.machine if insp else None)
        if machine:
            chain["nodes"]["machine"] = machine.to_dict()

        # 10. Process Step
        step = defect.process_step or (insp.process_step if insp else None)
        if step:
            chain["nodes"]["process_step"] = step.to_dict()

        # 11. Containment Actions
        cas = defect.containment_actions
        chain["nodes"]["containment_actions"] = [c.to_dict() for c in cas]

        # 12. Corrective Action & Verification
        capas = defect.corrective_actions
        chain["nodes"]["corrective_actions"] = [ca.to_dict() for ca in capas]
        if capas:
            latest_capa = capas[0]
            chain["nodes"]["verification_status"] = {
                "capa_id": latest_capa.id,
                "status": latest_capa.status,
                "is_verified": latest_capa.status in ("VERIFIED", "CLOSED"),
                "verification_date": latest_capa.verification_date.isoformat() if latest_capa.verification_date else None,
                "verified_by": latest_capa.verified_by,
                "closure_date": latest_capa.closure_date.isoformat() if latest_capa.closure_date else None
            }

        return chain

    @staticmethod
    def trace_product(product_id):
        product = db.session.get(Product, product_id)
        if not product:
            raise ValidationError(f"Product '{product_id}' not found.", code="NOT_FOUND")

        orders = product.production_orders
        defects = Defect.query.join(ProductionOrder).filter(ProductionOrder.product_id == product_id).all()
        
        return {
            "query_type": "product",
            "query_id": product_id,
            "product": product.to_dict(),
            "boms": [b.to_dict() for b in product.boms],
            "production_orders_count": len(orders),
            "production_orders": [o.to_dict() for o in orders[:25]],
            "total_defects_count": len(defects),
            "defects": [d.to_dict() for d in defects[:25]]
        }

    @staticmethod
    def trace_production_order(order_id):
        order = db.session.get(ProductionOrder, order_id)
        if not order:
            raise ValidationError(f"Production Order '{order_id}' not found.", code="NOT_FOUND")

        return {
            "query_type": "order",
            "query_id": order_id,
            "order": order.to_dict(),
            "product": order.product.to_dict() if order.product else None,
            "consumptions": [c.to_dict() for c in order.consumptions],
            "inspections": [i.to_dict() for i in order.inspections],
            "defects": [d.to_dict() for d in order.defects],
            "events": [e.to_dict() for e in order.production_events]
        }

    @staticmethod
    def trace_material_lot(lot_id):
        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise ValidationError(f"Material Lot '{lot_id}' not found.", code="NOT_FOUND")

        return {
            "query_type": "lot",
            "query_id": lot_id,
            "lot": lot.to_dict(),
            "supplier": lot.supplier.to_dict() if lot.supplier else None,
            "consumptions": [c.to_dict() for c in lot.consumptions],
            "defects": [d.to_dict() for d in lot.defects],
            "containment_actions": [ca.to_dict() for ca in lot.containment_actions]
        }

    @staticmethod
    def trace_supplier(supplier_id):
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            raise ValidationError(f"Supplier '{supplier_id}' not found.", code="NOT_FOUND")

        lots = supplier.material_lots
        lot_ids = [l.id for l in lots]
        defects = Defect.query.filter(Defect.material_lot_id.in_(lot_ids)).all() if lot_ids else []

        return {
            "query_type": "supplier",
            "query_id": supplier_id,
            "supplier": supplier.to_dict(),
            "lots_count": len(lots),
            "material_lots": [l.to_dict() for l in lots[:30]],
            "defects_count": len(defects),
            "defects": [d.to_dict() for d in defects[:30]]
        }

    @staticmethod
    def trace_machine(machine_id):
        machine = db.session.get(Machine, machine_id)
        if not machine:
            raise ValidationError(f"Machine '{machine_id}' not found.", code="NOT_FOUND")

        inspections = sorted(
            machine.inspections,
            key=lambda inspection: inspection.inspected_at,
            reverse=True
        )
        defects = sorted(
            machine.defects,
            key=lambda defect: defect.detected_at,
            reverse=True
        )

        return {
            "query_type": "machine",
            "query_id": machine_id,
            "machine": machine.to_dict(),
            "inspections_count": len(inspections),
            "inspections": [inspection.to_dict() for inspection in inspections[:30]],
            "defects_count": len(defects),
            "defects": [d.to_dict() for d in defects[:30]]
        }
