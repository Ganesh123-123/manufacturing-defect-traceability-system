from .api_master_data import bp as master_data_bp
from .api_production import bp as production_bp
from .api_inspection import bp as inspection_bp
from .api_defect import bp as defect_bp
from .api_capa import bp as capa_bp
from .api_traceability import bp as traceability_bp
from .api_analytics import bp as analytics_bp
from .api_system import bp as system_bp

def register_blueprints(app):
    app.register_blueprint(master_data_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(inspection_bp)
    app.register_blueprint(defect_bp)
    app.register_blueprint(capa_bp)
    app.register_blueprint(traceability_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(system_bp)

