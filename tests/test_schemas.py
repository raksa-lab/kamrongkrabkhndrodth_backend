import pytest
from pydantic import ValidationError
from app.schemas.book import BookCreate

def test_book_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        BookCreate(title="Test", price=-1)

def test_book_availability_is_limited():
    with pytest.raises(ValidationError):
        BookCreate(title="Test", price=1, availability="invalid")
