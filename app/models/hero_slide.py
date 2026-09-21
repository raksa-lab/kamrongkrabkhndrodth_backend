from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class HeroSlide(Base):
    __tablename__ = "hero_slides"
    __table_args__ = (CheckConstraint("position >= 0 AND position <= 2", name="ck_hero_slide_position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    image_url: Mapped[str] = mapped_column(String(1000), default="")
