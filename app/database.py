from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.models.models import Base
from app.config import config
import os

# Create database engine
def create_database_engine():
    database_url = config.database_url
    
    # For SQLite, ensure the directory exists
    if database_url.startswith('sqlite'):
        db_path = database_url.replace('sqlite:///', '')
        if db_path != ':memory:':
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Configure SQLite for better performance
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(database_url, echo=False)
    
    return engine

# Create engine instance
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables and default data"""
    create_tables()
    
    # Create default email config if none exists
    db = SessionLocal()
    try:
        from app.models.models import EmailConfig
        existing_config = db.query(EmailConfig).first()
        
        if not existing_config:
            email_config = config.email_config
            if email_config.get('username') and email_config.get('password'):
                default_config = EmailConfig(
                    smtp_host=email_config.get('smtp_host', 'smtp.gmail.com'),
                    smtp_port=email_config.get('smtp_port', 587),
                    username=email_config.get('username', ''),
                    password=email_config.get('password', ''),
                    from_email=email_config.get('from_email', ''),
                    use_tls=email_config.get('use_tls', True),
                    is_active=True
                )
                db.add(default_config)
                db.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close() 