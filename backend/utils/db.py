"""
Database Connection & Utilities
"""
from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

db = SQLAlchemy()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully")


def reset_db(app):
    """Drop all tables and recreate (for testing)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Database reset successfully")


@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    finally:
        db.session.close()


def commit_changes():
    """Commit all pending database changes"""
    db.session.commit()


def rollback_changes():
    """Rollback all pending changes"""
    db.session.rollback()


def execute_raw_sql(sql, params=None):
    """Execute raw SQL query"""
    try:
        if params:
            result = db.session.execute(db.text(sql), params)
        else:
            result = db.session.execute(db.text(sql))
        db.session.commit()
        return result
    except Exception as e:
        db.session.rollback()
        raise e


class BaseModel(db.Model):
    """Base model with common attributes"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())
    
    def save(self):
        """Save model to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete model from database"""
        db.session.delete(self)
        db.session.commit()
    
    def refresh(self):
        """Refresh model from database"""
        db.session.refresh(self)
        return self


# Import datetime for timestamps
from datetime import datetime
