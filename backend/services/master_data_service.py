from datetime import datetime
from backend.database.connection import db, get_session
from backend.models import Product, Supplier, BOM, Machine, ProcessStep, ProcessStepMachine
from backend.validation.exceptions import ValidationError

class MasterDataService:
    @staticmethod
    def get_products(page=1, per_page=50, search=None, category=None):
        query = Product.query
        if search:
            query = query.filter(Product.name.ilike(f"%{search}%") | Product.id.ilike(f"%{search}%"))
        if category:
            query = query.filter(Product.category == category)
        
        total = query.count()
        products = query.order_by(Product.id.asc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [p.to_dict() for p in products],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            raise ValidationError(f"Product {product_id} not found", code="NOT_FOUND")
        res = product.to_dict()
        res["boms"] = [b.to_dict() for b in product.boms]
        res["inspection_plans"] = [ip.to_dict() for ip in product.inspection_plans]
        return res

    @staticmethod
    def create_product(data):
        if not data.get("id") or not data.get("name"):
            raise ValidationError("Product id and name are required.")
        if Product.query.get(data["id"]):
            raise ValidationError(f"Product {data['id']} already exists.", code="DUPLICATE_KEY")
        
        with get_session() as session:
            product = Product(
                id=data["id"],
                name=data["name"],
                category=data.get("category", "General"),
                unit_of_measure=data.get("unit_of_measure", "PCS"),
                target_cycle_time_mins=float(data.get("target_cycle_time_mins", 15.0)),
                standard_cost=float(data.get("standard_cost", 0.0)),
                is_active=bool(data.get("is_active", True))
            )
            session.add(product)
            return product.to_dict()

    @staticmethod
    def get_suppliers(page=1, per_page=50, search=None, status=None):
        query = Supplier.query
        if search:
            query = query.filter(Supplier.name.ilike(f"%{search}%") | Supplier.id.ilike(f"%{search}%") | Supplier.code.ilike(f"%{search}%"))
        if status:
            query = query.filter(Supplier.status == status)
        
        total = query.count()
        suppliers = query.order_by(Supplier.id.asc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "items": [s.to_dict() for s in suppliers],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1
        }

    @staticmethod
    def get_supplier(supplier_id):
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            raise ValidationError(f"Supplier {supplier_id} not found", code="NOT_FOUND")
        res = supplier.to_dict()
        res["material_lots"] = [l.to_dict() for l in supplier.material_lots]
        return res

    @staticmethod
    def create_supplier(data):
        if not data.get("id") or not data.get("name") or not data.get("code"):
            raise ValidationError("Supplier id, name, and code are required.")
        if Supplier.query.get(data["id"]):
            raise ValidationError(f"Supplier {data['id']} already exists.", code="DUPLICATE_KEY")
        if Supplier.query.filter_by(code=data["code"]).first():
            raise ValidationError(f"Supplier code {data['code']} already in use.", code="DUPLICATE_KEY")
        
        with get_session() as session:
            supplier = Supplier(
                id=data["id"],
                name=data["name"],
                code=data["code"],
                contact_email=data.get("contact_email"),
                contact_phone=data.get("contact_phone"),
                country=data.get("country", "USA"),
                rating=float(data.get("rating", 4.5)),
                status=data.get("status", "ACTIVE")
            )
            session.add(supplier)
            return supplier.to_dict()

    @staticmethod
    def get_boms(parent_product_id=None):
        query = BOM.query
        if parent_product_id:
            query = query.filter_by(parent_product_id=parent_product_id)
        return [b.to_dict() for b in query.all()]

    @staticmethod
    def create_bom(data):
        if not data.get("parent_product_id") or not data.get("component_sku") or not data.get("component_name"):
            raise ValidationError("Parent product ID, component SKU, and component name are required.")
        product = Product.query.get(data["parent_product_id"])
        if not product:
            raise ValidationError(f"Parent product {data['parent_product_id']} does not exist.")
        
        qty = float(data.get("quantity_per_unit", 1.0))
        if qty <= 0:
            raise ValidationError("quantity_per_unit must be strictly greater than 0.")
        
        with get_session() as session:
            bom = BOM(
                parent_product_id=data["parent_product_id"],
                component_sku=data["component_sku"],
                component_name=data["component_name"],
                quantity_per_unit=qty,
                unit_of_measure=data.get("unit_of_measure", "PCS"),
                scrap_factor=float(data.get("scrap_factor", 0.0)),
                revision=data.get("revision", "1.0"),
                effective_from=datetime.utcnow()
            )
            session.add(bom)
            session.flush()
            return bom.to_dict()

    @staticmethod
    def get_machines():
        machines = Machine.query.order_by(Machine.line.asc(), Machine.machine_code.asc()).all()
        return [m.to_dict() for m in machines]

    @staticmethod
    def create_machine(data):
        if not data.get("id") or not data.get("machine_code") or not data.get("name"):
            raise ValidationError("id, machine_code, and name are required.")
        with get_session() as session:
            m = Machine(
                id=data["id"],
                machine_code=data["machine_code"],
                name=data["name"],
                type=data.get("type", "CNC"),
                line=data.get("line", "Line-A"),
                location=data.get("location", "Main Plant"),
                status=data.get("status", "OPERATIONAL")
            )
            session.add(m)
            return m.to_dict()

    @staticmethod
    def get_process_steps():
        steps = ProcessStep.query.order_by(ProcessStep.sequence_number.asc()).all()
        return [s.to_dict() for s in steps]

    @staticmethod
    def create_process_step(data):
        if not data.get("id") or not data.get("step_code") or not data.get("name"):
            raise ValidationError("id, step_code, and name are required.")
        with get_session() as session:
            s = ProcessStep(
                id=data["id"],
                step_code=data["step_code"],
                name=data["name"],
                sequence_number=int(data.get("sequence_number", 10)),
                standard_duration_mins=float(data.get("standard_duration_mins", 15.0)),
                inspection_required=bool(data.get("inspection_required", True)),
                description=data.get("description", "")
            )
            session.add(s)
            return s.to_dict()
