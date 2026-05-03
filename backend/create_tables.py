from app.database import engine, Base
import app.models  # registers all models with Base before creating tables

Base.metadata.create_all(bind=engine)
print("All tables created successfully.")
print("Tables:", list(Base.metadata.tables.keys()))
