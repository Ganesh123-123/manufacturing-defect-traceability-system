import os
import json
import csv
from datetime import datetime

class DataExporter:
    @staticmethod
    def export_all(dataset, export_dir="backend/exports"):
        os.makedirs(export_dir, exist_ok=True)
        manifest = {
            "system": "Manufacturing Defect Traceability & Quality Management System",
            "export_timestamp": datetime.utcnow().isoformat(),
            "exported_tables": list(dataset.keys()),
            "table_counts": {k: len(v) for k, v in dataset.items()},
            "files": []
        }

        # 1. Export JSON & CSV for every entity table
        for table_name, records in dataset.items():
            if not records:
                continue

            # JSON export
            json_filename = f"{table_name}.json"
            json_path = os.path.join(export_dir, json_filename)
            # Serialize datetimes to isoformat string
            clean_records = []
            for r in records:
                clean_r = {}
                for k, v in r.items():
                    if isinstance(v, datetime):
                        clean_r[k] = v.isoformat()
                    else:
                        clean_r[k] = v
                clean_records.append(clean_r)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(clean_records, f, indent=2)
            manifest["files"].append(json_filename)

            # CSV export
            csv_filename = f"{table_name}.csv"
            csv_path = os.path.join(export_dir, csv_filename)
            keys = list(clean_records[0].keys())
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(clean_records)
            manifest["files"].append(csv_filename)

        # 2. Export SQL Seed Data
        sql_filename = "seed_data.sql"
        sql_path = os.path.join(export_dir, sql_filename)
        DataExporter.export_sql(dataset, sql_path)
        manifest["files"].append(sql_filename)

        # 3. Export Data Dictionary
        DataExporter.export_data_dictionary(export_dir)
        manifest["files"].append("data_dictionary.json")

        # 4. Export Database Schema DDL
        DataExporter.export_schema_ddl(export_dir)
        manifest["files"].append("schema.sql")

        # 5. Export Source Manifest
        manifest_path = os.path.join(export_dir, "source_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    @staticmethod
    def export_sql(dataset, sql_path):
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write("-- Manufacturing Defect Traceability System Seed Data\n")
            f.write(f"-- Generated at {datetime.utcnow().isoformat()}\n\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

            for table_name, records in dataset.items():
                if not records:
                    continue
                f.write(f"-- Table: {table_name}\n")
                keys = list(records[0].keys())
                col_str = ", ".join([f"`{k}`" for k in keys])
                for r in records[:500]:  # sample top 500 records per table to keep seed_data.sql manageable
                    vals = []
                    for k in keys:
                        v = r[k]
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, bool):
                            vals.append("1" if v else "0")
                        elif isinstance(v, datetime):
                            vals.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
                        else:
                            clean_str = str(v).replace("'", "''").replace("\\", "\\\\")
                            vals.append(f"'{clean_str}'")
                    val_str = ", ".join(vals)
                    f.write(f"INSERT INTO `{table_name}` ({col_str}) VALUES ({val_str});\n")
                f.write("\n")

            f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    @staticmethod
    def export_data_dictionary(export_dir):
        dictionary = {
            "entities": {
                "products": {
                    "description": "Catalog of manufactured items and end products",
                    "id_format": "SKU-000001",
                    "fields": {
                        "id": "Primary Key, SKU code",
                        "name": "Full product nomenclature",
                        "category": "Industrial classification",
                        "target_cycle_time_mins": "Target takt/cycle time in minutes",
                        "standard_cost": "Baseline manufacturing standard cost in USD"
                    }
                },
                "suppliers": {
                    "description": "Approved material and raw component vendors",
                    "id_format": "SUP-000001",
                    "fields": {
                        "id": "Primary Key, Supplier ID",
                        "name": "Company trading name",
                        "code": "Unique vendor identifier (e.g. VEND-0001)",
                        "rating": "Vendor quality rating (1.0 - 5.0)"
                    }
                },
                "material_lots": {
                    "description": "Received batches of components with pedigree",
                    "id_format": "LOT-SUP-000001-2026-000001",
                    "fields": {
                        "id": "Primary Key, Unique Lot Number",
                        "supplier_id": "Foreign Key to suppliers",
                        "initial_quantity": "Received quantity",
                        "remaining_quantity": "Current available unconsumed quantity"
                    }
                },
                "production_orders": {
                    "description": "Shop floor work orders authorizing assembly",
                    "id_format": "WO-2026-000001",
                    "fields": {
                        "id": "Primary Key, Work Order ID",
                        "product_id": "Foreign Key to products",
                        "target_quantity": "Planned batch units",
                        "completed_quantity": "Passed conforming units",
                        "rework_quantity": "Reworked units",
                        "scrapped_quantity": "Scrapped non-conforming units"
                    }
                },
                "inspection_results": {
                    "description": "Quality control inspection gate records",
                    "id_format": "INSP-WO-2026-000001-001",
                    "fields": {
                        "id": "Primary Key, Inspection Result ID",
                        "production_order_id": "Foreign Key to production_orders",
                        "inspected_quantity": "Units examined",
                        "passed_quantity": "Conforming units",
                        "failed_quantity": "Non-conforming units",
                        "result": "PASS / FAIL / CONDITIONAL_PASS"
                    }
                },
                "defects": {
                    "description": "Non-conformance incident records",
                    "id_format": "DEF-2026-000001",
                    "fields": {
                        "id": "Primary Key, Defect ID",
                        "inspection_result_id": "Foreign Key to inspection_results",
                        "material_lot_id": "Foreign Key to material_lots (traceability root)",
                        "severity": "CRITICAL / MAJOR / MINOR",
                        "disposition": "REWORK / SCRAP / USE_AS_IS / RETURN_TO_VENDOR"
                    }
                },
                "corrective_actions": {
                    "description": "CAPA investigation, containment, and verification records",
                    "id_format": "CAPA-2026-000001",
                    "fields": {
                        "id": "Primary Key, CAPA ID",
                        "defect_id": "Foreign Key to defects",
                        "status": "OPEN / IN_PROGRESS / CONTAINMENT / PENDING_VERIFICATION / VERIFIED / CLOSED",
                        "verification_date": "Timestamp of formal verification before closure"
                    }
                }
            }
        }
        with open(os.path.join(export_dir, "data_dictionary.json"), "w", encoding="utf-8") as f:
            json.dump(dictionary, f, indent=2)

    @staticmethod
    def export_schema_ddl(export_dir):
        schema_sql = """-- Database Schema DDL for Manufacturing Defect Traceability System
-- Compatible with MySQL 8.0+

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    unit_of_measure VARCHAR(20) DEFAULT 'PCS',
    target_cycle_time_mins FLOAT DEFAULT 15.0,
    standard_cost FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_cat (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS suppliers (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    contact_email VARCHAR(120),
    contact_phone VARCHAR(50),
    country VARCHAR(80) DEFAULT 'USA',
    rating FLOAT DEFAULT 4.5,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS material_lots (
    id VARCHAR(64) PRIMARY KEY,
    supplier_id VARCHAR(32) NOT NULL,
    material_sku VARCHAR(64) NOT NULL,
    material_name VARCHAR(150) NOT NULL,
    batch_number VARCHAR(64) NOT NULL,
    initial_quantity FLOAT NOT NULL,
    remaining_quantity FLOAT NOT NULL,
    unit_of_measure VARCHAR(20) DEFAULT 'PCS',
    received_date DATETIME NOT NULL,
    expiry_date DATETIME,
    certificate_of_analysis VARCHAR(100),
    status VARCHAR(30) DEFAULT 'RELEASED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    INDEX idx_lot_mat (material_sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS production_orders (
    id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL,
    target_quantity INT NOT NULL,
    completed_quantity INT DEFAULT 0,
    scrapped_quantity INT DEFAULT 0,
    rework_quantity INT DEFAULT 0,
    status VARCHAR(30) DEFAULT 'PLANNED',
    planned_start_date DATETIME,
    planned_end_date DATETIME,
    actual_start_date DATETIME,
    actual_end_date DATETIME,
    batch_number VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_wo_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS inspection_results (
    id VARCHAR(64) PRIMARY KEY,
    inspection_plan_id VARCHAR(64) NOT NULL,
    production_order_id VARCHAR(32) NOT NULL,
    step_id VARCHAR(32),
    machine_id VARCHAR(32),
    inspected_quantity INT NOT NULL,
    passed_quantity INT NOT NULL DEFAULT 0,
    failed_quantity INT NOT NULL DEFAULT 0,
    result VARCHAR(30) DEFAULT 'PASS',
    inspected_at DATETIME NOT NULL,
    inspector_name VARCHAR(100),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS defects (
    id VARCHAR(32) PRIMARY KEY,
    inspection_result_id VARCHAR(64) NOT NULL,
    production_order_id VARCHAR(32) NOT NULL,
    material_lot_id VARCHAR(64),
    machine_id VARCHAR(32),
    step_id VARCHAR(32),
    defect_code VARCHAR(32) NOT NULL,
    defect_type VARCHAR(80) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    defect_quantity INT NOT NULL,
    disposition VARCHAR(30) DEFAULT 'REWORK',
    rework_quantity INT DEFAULT 0,
    scrap_quantity INT DEFAULT 0,
    root_cause_category VARCHAR(50) DEFAULT 'MATERIAL',
    description TEXT,
    status VARCHAR(30) DEFAULT 'IDENTIFIED',
    detected_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_result_id) REFERENCES inspection_results(id),
    FOREIGN KEY (production_order_id) REFERENCES production_orders(id),
    INDEX idx_defect_code (defect_code),
    INDEX idx_defect_sev (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS corrective_actions (
    id VARCHAR(32) PRIMARY KEY,
    defect_id VARCHAR(32) NOT NULL,
    containment_action_id INT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    root_cause_analysis TEXT,
    corrective_action_plan TEXT,
    preventive_action_plan TEXT,
    status VARCHAR(30) DEFAULT 'OPEN',
    assigned_to VARCHAR(100),
    target_date DATETIME,
    verification_date DATETIME,
    verified_by VARCHAR(100),
    verification_notes TEXT,
    closure_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (defect_id) REFERENCES defects(id),
    INDEX idx_capa_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
        with open(os.path.join(export_dir, "schema.sql"), "w", encoding="utf-8") as f:
            f.write(schema_sql)

