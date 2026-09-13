import pytest
from pydantic import ValidationError
from app.schemas.book import BookCreate
from app.core.config import Settings


def test_cors_origins_are_parsed_from_comma_separated_setting():
    settings = Settings(cors_origins=" https://store.example.com, ,http://localhost:3000 ")

    assert settings.cors_origins_list == [
        "https://store.example.com",
        "http://localhost:3000",
    ]

def test_book_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        BookCreate(title="Test", price=-1)

def test_book_availability_is_limited():
    with pytest.raises(ValidationError):
        BookCreate(title="Test", price=1, availability="invalid")
