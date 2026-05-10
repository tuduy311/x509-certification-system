from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.core import security
from app.core.config import settings
from app.db.database import engine

models.Base.metadata.create_all(bind=engine)


def init_db(db: Session) -> None:
    # Lấy Admin credential từ .env file qua settings object
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD
    
    user = db.query(models.User).filter(models.User.username == admin_username).first()
    if not user:
        user = models.User(
            username=admin_username,
            hashed_password=security.get_password_hash(admin_password),
            role=models.Role.ADMIN
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Admin user '{admin_username}' created successfully")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database initialization complete.")
