import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Availability(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    COMING_SOON = "COMING_SOON"

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="General", index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str] = mapped_column(String(1000), default="")
    availability: Mapped[Availability] = mapped_column(Enum(Availability), default=Availability.AVAILABLE, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
