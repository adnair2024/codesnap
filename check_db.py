import os
import sys
from sqlalchemy import create_engine, text

def check_connection():
    db_url = os.environ.get('DATABASE_URL', '').strip()
    if not db_url:
        print("❌ DATABASE_URL is not set or empty.")
        db_url = 'sqlite:///snippets.db'
        print(f"   Using default: {db_url}")
    else:
        print(f"ℹ️  Found DATABASE_URL (length: {len(db_url)})")
        # Mask password for display
        if '@' in db_url:
            masked = db_url.split('@')[1]
            print(f"   Target host: ...@{masked}")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Successfully connected to the database!")
            print(f"   Test Query Result: {result.scalar()}")
    except Exception as e:
        print("\n❌ CONNECTION FAILED:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    check_connection()
