from src.database.connection import init_db
import os

# Ensure your .env is loaded (if not already handled by codespaces)
print(f"Connecting to: {os.environ.get('DATABASE_URL')[:20]}...") 
init_db()