from app import app, db
import os

with app.app_context():
    db_path = os.path.join(app.instance_path, 'snippets.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Deleted old database: {db_path}")
    elif os.path.exists('snippets.db'):
        os.remove('snippets.db')
        print("🗑️  Deleted old database: snippets.db")
    
    db.create_all()
    print("✅ Created fresh database tables (User, Snippet, Vote).")
    print("ℹ️  You will need to register a new user.")
