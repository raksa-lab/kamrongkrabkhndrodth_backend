from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.book import Availability

class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(default="", max_length=255)
    description: str = ""
    category: str = Field(default="General", max_length=100)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    image_url: str = ""
    availability: Availability = Availability.AVAILABLE

class BookCreate(BookBase):
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = None
    description: str | None = None
    category: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    image_url: str | None = None
    availability: Availability | None = None

class BookOut(BookBase):
    id: int
    slug: str
    model_config = ConfigDict(from_attributes=True)

class BookList(BaseModel):
    items: list[BookOut]
    total: int
    page: int
    page_size: int
