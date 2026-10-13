from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, LargeBinary, String
from app.db.session import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    filename = Column(String, unique=True, index=True, nullable=False)
    content_type = Column(String, nullable=False, default="image/jpeg")
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
