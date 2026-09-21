from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models.hero_slide import HeroSlide
from app.schemas.hero_slide import HeroSlideList, HeroSlideOut, HeroSlideUpdate

public_router = APIRouter(prefix="/api/hero-slides", tags=["hero-slides"])
admin_router = APIRouter(prefix="/api/admin/hero-slides", tags=["admin-hero-slides"], dependencies=[Depends(get_current_admin)])


def ordered_slides(db: Session) -> list[HeroSlide]:
    existing = {slide.position: slide for slide in db.query(HeroSlide).all()}
    missing = [HeroSlide(position=position, image_url="") for position in range(3) if position not in existing]
    if missing:
        db.add_all(missing)
        db.commit()
        existing.update({slide.position: slide for slide in missing})
    return [existing[position] for position in range(3)]


@public_router.get("", response_model=HeroSlideList)
def list_public_slides(db: Session = Depends(get_db)):
    return HeroSlideList(items=ordered_slides(db))


@admin_router.get("", response_model=HeroSlideList)
def list_admin_slides(db: Session = Depends(get_db)):
    return HeroSlideList(items=ordered_slides(db))


@admin_router.put("/{position}", response_model=HeroSlideOut)
def update_admin_slide(position: int, payload: HeroSlideUpdate, db: Session = Depends(get_db)):
    slide = db.query(HeroSlide).filter(HeroSlide.position == position).first()
    if not slide:
        slide = HeroSlide(position=position)
        db.add(slide)
    slide.image_url = payload.image_url
    db.commit()
    db.refresh(slide)
    return slide
