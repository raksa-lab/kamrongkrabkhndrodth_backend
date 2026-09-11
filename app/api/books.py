from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.book import Availability, Book
from app.schemas.book import BookList, BookOut

router = APIRouter(prefix="/api/books", tags=["books"])

@router.get("", response_model=BookList)
def list_books(search: str | None = None, category: str | None = None, availability: Availability | None = None, page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(Book)
    if search:
        term = f"%{search}%"
        query = query.filter(or_(Book.title.ilike(term), Book.author.ilike(term), Book.description.ilike(term)))
    if category:
        query = query.filter(Book.category == category)
    if availability:
        query = query.filter(Book.availability == availability)
    total = query.count()
    items = query.order_by(Book.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return BookList(items=items, total=total, page=page, page_size=page_size)

@router.get("/{slug}", response_model=BookOut)
def get_book(slug: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.slug == slug).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
