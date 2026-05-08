from core.database import engine, Base
from models.destination import Destination
from models.user import User # Assuming this exists or will exist

def init_db():
    print("Initializing PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
