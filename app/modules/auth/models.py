from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id= Column(Integer, primary_key=True, index=True)
    username=Column(String, unique=True, nullable=False)
    email=Column(String, nullable=False)
    hashed_password= Column(String, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
