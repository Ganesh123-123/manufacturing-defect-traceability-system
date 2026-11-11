from backend.time_utils import utcnow
from backend.database.connection import db, get_session
from backend.models import (
    MaterialLot, ProductionOrder, Product, Supplier, BOM,
    MaterialConsumption, ProductionEvent, ProductionOrderMaterial
)
from backend.validation.exceptions import (
    ValidationError,
    MaterialReconciliationException
)
from backend.validation.rules import validate_material_consumption_reconciliation

class ProductionService:
    @staticmethod
    def get_material_lots(page=1, per_page=50, search=None, status=None, supplier_id=None):
        query = MaterialLot.query
        if search:
            query = query.filter(
                MaterialLot.id.ilike(f"%{search}%") |
                MaterialLot.material_name.ilike(f"%{search}%") |
                MaterialLot.batch_number.ilike(f"%{search}%")
            )
        if status:
            query = query.filter(MaterialLot.status == status)
        if supplier_id:
            query = query.filter(MaterialLot.supplier_id == supplier_id)
        
        total = query.count()
        lots = query.order_by(MaterialLot.received_date.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [l.to_dict() for l in lots],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_material_lot(lot_id):
        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise ValidationError(f"Material Lot {lot_id} not found", code="NOT_FOUND")
        res = lot.to_dict()
        res["consumptions"] = [c.to_dict() for c in lot.consumptions]
        res["defects"] = [d.to_dict() for d in lot.defects]
        res["containment_actions"] = [ca.to_dict() for ca in lot.containment_actions]
        return res

    @staticmethod
    def create_material_lot(data):
        # Rule 2: Material lots must reference valid suppliers
        supplier_id = data.get("supplier_id")
        if not supplier_id or not db.session.get(Supplier, supplier_id):
            raise ValidationError(f"Valid supplier_id is required. Supplier {supplier_id} not found.")

        lot_id = data.get("id")
        if not lot_id or not data.get("material_sku") or not data.get("material_name"):
            raise ValidationError("id, material_sku, and material_name are required.")
        
        if db.session.get(MaterialLot, lot_id):
            raise ValidationError(f"Material Lot {lot_id} already exists.", code="DUPLICATE_KEY")

        qty = float(data.get("initial_quantity", 1000.0))
        if qty <= 0:
            raise ValidationError("initial_quantity must be greater than 0.")

        with get_session() as session:
            lot = MaterialLot(
                id=lot_id,
                supplier_id=supplier_id,
                material_sku=data["material_sku"],
                material_name=data["material_name"],
                batch_number=data.get("batch_number", f"BATCH-{lot_id}"),
                initial_quantity=qty,
                remaining_quantity=qty,
                unit_of_measure=data.get("unit_of_measure", "PCS"),
                received_date=utcnow(),
                certificate_of_analysis=data.get("certificate_of_analysis", "COA-VALIDATED"),
                status=data.get("status", "RELEASED")
            )
            session.add(lot)
            return lot.to_dict()

    @staticmethod
    def get_production_orders(page=1, per_page=50, search=None, status=None, product_id=None):
        query = ProductionOrder.query
        if search:
            query = query.filter(
                ProductionOrder.id.ilike(f"%{search}%") |
                ProductionOrder.product_id.ilike(f"%{search}%") |
                ProductionOrder.batch_number.ilike(f"%{search}%")
            )
        if status:
            query = query.filter(ProductionOrder.status == status)
        if product_id:
            query = query.filter(ProductionOrder.product_id == product_id)
        
        total = query.count()
        orders = query.order_by(ProductionOrder.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [o.to_dict() for o in orders],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_production_order(order_id):
        order = db.session.get(ProductionOrder, order_id)
        if not order:
            raise ValidationError(f"Production Order {order_id} not found", code="NOT_FOUND")
        res = order.to_dict()
        res["consumptions"] = [c.to_dict() for c in order.consumptions]
        res["inspections"] = [i.to_dict() for i in order.inspections]
        res["defects"] = [d.to_dict() for d in order.defects]
        res["events"] = [e.to_dict() for e in order.production_events]
        return res

    @staticmethod
    def create_production_order(data):
        # Rule 1: Production orders must reference valid products
        product_id = data.get("product_id")
        product = db.session.get(Product, product_id)
        if not product_id or not product:
            raise ValidationError(f"Valid product_id is required. Product {product_id} not found.")

        order_id = data.get("id")
        if not order_id:
            raise ValidationError("Production order id is required.")
        
        if db.session.get(ProductionOrder, order_id):
            raise ValidationError(f"Production Order {order_id} already exists.", code="DUPLICATE_KEY")

        target_qty = int(data.get("target_quantity", 100))
        if target_qty <= 0:
            raise ValidationError("target_quantity must be greater than 0.")

        with get_session() as session:
            order = ProductionOrder(
                id=order_id,
                product_id=product_id,
                target_quantity=target_qty,
                completed_quantity=0,
                scrapped_quantity=0,
                rework_quantity=0,
                status=data.get("status", "PLANNED"),
                batch_number=data.get("batch_number", f"BATCH-{order_id}"),
                planned_start_date=utcnow()
            )
            session.add(order)

            # Record event
            event = ProductionEvent(
                production_order_id=order_id,
                event_type="CREATED",
                status_from=None,
                status_to="PLANNED",
                details=f"Production order created for product {product_id} with target {target_qty}."
            )
            session.add(event)

            # Pre-plan BOM requirements
            for bom in product.boms:
                req_qty = bom.quantity_per_unit * target_qty * (1.0 + bom.scrap_factor)
                pom = ProductionOrderMaterial(
                    production_order_id=order_id,
                    bom_id=bom.id,
                    material_sku=bom.component_sku,
                    required_quantity=req_qty,
                    allocated_quantity=req_qty,
                    consumed_quantity=0.0,
                    unit_of_measure=bom.unit_of_measure
                )
                session.add(pom)

            return order.to_dict()

    @staticmethod
    def record_material_consumption(data):
        # Rule 3: Material consumption must reference valid lots and production orders
        order_id = data.get("production_order_id")
        lot_id = data.get("material_lot_id")
        consumed_qty = float(data.get("consumed_quantity", 0.0))

        order = db.session.get(ProductionOrder, order_id)
        if not order:
            raise ValidationError(f"Production order {order_id} not found.")

        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise ValidationError(f"Material lot {lot_id} not found.")

        if consumed_qty <= 0:
            raise ValidationError("consumed_quantity must be greater than 0.")

        if lot.remaining_quantity < consumed_qty:
            raise MaterialReconciliationException(
                f"Insufficient lot quantity. Available: {lot.remaining_quantity}, requested: {consumed_qty}"
            )

        bom_id = data.get("bom_id")

        with get_session() as session:
            consumption = MaterialConsumption(
                production_order_id=order_id,
                material_lot_id=lot_id,
                bom_id=bom_id,
                consumed_quantity=consumed_qty,
                unit_of_measure=data.get("unit_of_measure", lot.unit_of_measure),
                consumed_at=utcnow()
            )
            session.add(consumption)

            # Decrement lot remaining
            lot.remaining_quantity -= consumed_qty
            if lot.remaining_quantity <= 0:
                lot.status = "CONSUMED"

            # Update planned material if linked
            if bom_id:
                pom = ProductionOrderMaterial.query.filter_by(
                    production_order_id=order_id, bom_id=bom_id
                ).first()
                if pom:
                    pom.consumed_quantity += consumed_qty

            return consumption.to_dict()
