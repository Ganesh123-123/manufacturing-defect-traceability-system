import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.database.connection import db, init_db
from backend.routes import register_blueprints

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("manufacturing_backend")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Initialize Database
    init_db(app)

    # Register API Blueprints
    register_blueprints(app)

    @app.route("/")
    def index():
        return jsonify({
            "service": "Manufacturing Defect Traceability & Quality Management System API",
            "version": "1.0.0",
            "status": "online",
            "docs": "/docs",
            "api_prefix": "/api"
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found", "code": "NOT_FOUND"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "An internal server error occurred", "code": "INTERNAL_ERROR"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Manufacturing Defect Traceability API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
