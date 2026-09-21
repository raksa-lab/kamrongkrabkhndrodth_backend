import pytest
from pydantic import ValidationError

from app.schemas.hero_slide import HeroSlideUpdate


def test_hero_slide_update_accepts_image_url():
    assert HeroSlideUpdate(image_url="/uploads/hero.jpg").image_url == "/uploads/hero.jpg"


def test_hero_slide_update_rejects_oversized_image_url():
    with pytest.raises(ValidationError):
        HeroSlideUpdate(image_url="x" * 1001)
