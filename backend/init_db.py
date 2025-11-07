"""
Database initialization script
Run this to create the users table and add test users
"""
from sqlalchemy import text
from database import engine
from models import Base, User
from auth import get_password_hash

def init_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def add_test_user():
    """Add a test user to the database"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists!")
            return

        # Create test user
        hashed_password = get_password_hash("password123")
        test_user = User(
            email="test@example.com",
            hashed_password=hashed_password
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Test user created successfully!")
        print(f"Email: test@example.com")
        print(f"Password: password123")

    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    add_test_user()
