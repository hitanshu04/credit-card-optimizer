import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# 1. Load .env file first
load_dotenv()

# 2. Pick URL from .env file.
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL nahi mila! .env file check karo.")

# 3. Engine: Actual Connection engine that talks to Neon
# 'pool_pre_ping' checks if connection is alive or not.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 4. SessionLocal: Helps to enter into db (Insert/Update)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Creates tables on Neon in accordance with 'models.py'.
    """
    print("      -> Initializing Database Tables on Neon.tech...")
    try:
        # Base.metadata.create_all creates CreditCard table on 
        Base.metadata.create_all(bind=engine)
        print("      -> [SUCCESS] Tables created successfully!")
    except Exception as e:
        print(f"      -> [ERROR] DB Initialization failed: {e}")

def get_db():
    """
    Utility function to provide Database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()