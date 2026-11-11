import os
import sys
import argparse
import json
import logging

# Ensure root workspace and backend are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.generator.data_factory import DataFactory
from backend.generator.anomaly_injector import AnomalyInjector
from backend.generator.exporter import DataExporter
from backend.generator.reproducibility import ReproducibilityVerifier
from backend.database.connection import db
from backend.validation.rules import run_full_database_validation
from backend.models import (
    Product, Supplier, MaterialLot, ProductionOrder, BOM, Machine,
    ProcessStep, ProcessStepMachine, InspectionPlan, InspectionResult,
    Defect, ContainmentAction, CorrectiveAction, MaterialConsumption,
    ProductionOrderMaterial, ProductionEvent, DefectEvent, CorrectiveActionEvent
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataGenerator")

MODEL_MAP = {
    "products": Product,
    "suppliers": Supplier,
    "material_lots": MaterialLot,
    "boms": BOM,
    "machines": Machine,
    "process_steps": ProcessStep,
    "step_machines": ProcessStepMachine,
    "inspection_plans": InspectionPlan,
    "production_orders": ProductionOrder,
    "material_consumptions": MaterialConsumption,
    "production_events": ProductionEvent,
    "inspections": InspectionResult,
    "defects": Defect,
    "containment_actions": ContainmentAction,
    "corrective_actions": CorrectiveAction,
    "defect_events": DefectEvent,
    "capa_events": CorrectiveActionEvent
}

def load_data_into_db(dataset, app=None):
    from backend.app import create_app
    if app is None:
        app = create_app()

    with app.app_context():
        logger.info("Initializing database tables...")
        # Disable foreign key checks for synthetic test dataset loading (to allow injected anomaly FKs)
        if db.engine.name == "mysql":
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
        elif db.engine.name == "sqlite":
            db.session.execute(db.text("PRAGMA foreign_keys = OFF;"))
        db.session.commit()

        db.create_all()

        # Clear existing data in reverse dependency order
        for table_key in reversed(list(MODEL_MAP.keys())):
            model = MODEL_MAP[table_key]
            try:
                db.session.query(model).delete()
            except Exception as e:
                logger.debug(f"Clear table {table_key}: {e}")
        db.session.commit()

        # Insert records in dependency order
        logger.info("Inserting generated records into database...")
        for table_key, model in MODEL_MAP.items():
            records = dataset.get(table_key, [])
            if not records:
                continue
            
            # Batch inserts for speed
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                objs = [model(**r) for r in batch]
                db.session.bulk_save_objects(objs)
                db.session.commit()
            logger.info(f"Loaded {len(records)} records into {table_key}")

        # Re-enable foreign key checks
        if db.engine.name == "mysql":
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1;"))
        elif db.engine.name == "sqlite":
            db.session.execute(db.text("PRAGMA foreign_keys = ON;"))
        db.session.commit()

        # Run validation
        logger.info("Running post-generation database validation audit...")
        summary = run_full_database_validation(db.session)
        logger.info(f"Validation Status: {summary['validation_status']} (Total checks: {summary['total_checks']}, Failed checks: {summary['failed_checks']})")
        return summary

def generate_dataset(scale="starter", seed=20261022, inject_anomalies=True, populate_db=True, export_dir="backend/exports"):
    os.makedirs(export_dir, exist_ok=True)
    logger.info(f"Starting synthetic data generation (Scale: {scale}, Seed: {seed})...")

    # Step 1: Generate valid baseline data
    factory = DataFactory(seed=seed)
    dataset = factory.generate_all(scale=scale)
    logger.info(f"Baseline generation complete: {len(dataset['products'])} products, {len(dataset['suppliers'])} suppliers, {len(dataset['material_lots'])} lots, {len(dataset['production_orders'])} orders, {len(dataset['inspections'])} inspections.")

    # Step 2: Inject labelled anomalies (Section 12)
    injector = AnomalyInjector()
    if inject_anomalies:
        logger.info("Injecting 5 controlled anomaly scenarios...")
        dataset, ground_truth = injector.inject_anomalies(dataset)
        json_gt, csv_gt = injector.export_ground_truth(export_dir)
        logger.info(f"Ground truth exported to {json_gt} and {csv_gt}")

    # Step 3: Populate DB
    validation_summary = None
    if populate_db:
        try:
            validation_summary = load_data_into_db(dataset)
            val_path = os.path.join(export_dir, "validation_summary.json")
            with open(val_path, "w", encoding="utf-8") as f:
                json.dump(validation_summary, f, indent=2)
            logger.info(f"Validation summary saved to {val_path}")
        except Exception as e:
            logger.error(f"Failed to populate database: {e}")

    # Step 4: Export artifacts (Section 18)
    logger.info("Exporting CSV, JSON, SQL seed, and manifests...")
    manifest = DataExporter.export_all(dataset, export_dir)

    # Step 5: Verify Reproducibility (Section 16)
    logger.info("Running automated reproducibility verification...")
    rep_report = ReproducibilityVerifier.verify(seed=seed, scale="starter")
    rep_path = os.path.join(export_dir, "reproducibility_report.json")
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(rep_report, f, indent=2)
    logger.info(f"Reproducibility report saved to {rep_path} (Status: {'REPRODUCIBLE' if rep_report['is_reproducible'] else 'FAILED'})")

    return {
        "dataset": dataset,
        "manifest": manifest,
        "validation_summary": validation_summary,
        "reproducibility_report": rep_report
    }

def main():
    parser = argparse.ArgumentParser(description="Manufacturing Defect Traceability Synthetic Data Generator")
    parser.add_argument("--scale", choices=["starter", "full"], default="starter", help="Dataset scale: starter or full")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed (default: 20261022)")
    parser.add_argument("--no-anomalies", action="store_true", help="Skip anomaly injection")
    parser.add_argument("--no-db", action="store_true", help="Skip database insertion")
    parser.add_argument("--export-dir", default="backend/exports", help="Export directory path")
    parser.add_argument("--verify-reproducibility", action="store_true", help="Only run reproducibility verification")

    args = parser.parse_args()

    if args.verify_reproducibility:
        rep_report = ReproducibilityVerifier.verify(seed=args.seed, scale=args.scale)
        print(json.dumps(rep_report, indent=2))
        sys.exit(0 if rep_report["is_reproducible"] else 1)

    generate_dataset(
        scale=args.scale,
        seed=args.seed,
        inject_anomalies=not args.no_anomalies,
        populate_db=not args.no_db,
        export_dir=args.export_dir
    )

if __name__ == "__main__":
    main()
