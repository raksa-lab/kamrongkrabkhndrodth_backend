from pydantic import BaseModel, Field


class HeroSlideUpdate(BaseModel):
    image_url: str = Field(default="", max_length=1000)


class HeroSlideOut(BaseModel):
    position: int
    image_url: str

    model_config = {"from_attributes": True}


class HeroSlideList(BaseModel):
    items: list[HeroSlideOut]
