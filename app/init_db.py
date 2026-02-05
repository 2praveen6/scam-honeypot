from app.db import engine, Base
from app.db_models import HoneypotSession

def init_database():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized!")

if __name__ == "__main__":
    init_database()