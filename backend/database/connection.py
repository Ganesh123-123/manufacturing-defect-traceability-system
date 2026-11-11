from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables verified/created successfully.")
        except Exception as e:
            logger.warning(f"Could not immediately initialize database tables: {e}")

@contextmanager
def get_session():
    """Transactional scope around a series of operations."""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise

