-- Database Schema DDL for Manufacturing Defect Traceability System
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
