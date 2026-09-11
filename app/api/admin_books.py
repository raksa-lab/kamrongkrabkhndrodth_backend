import re
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookList, BookOut, BookUpdate

router = APIRouter(prefix="/api/admin/books", tags=["admin-books"], dependencies=[Depends(get_current_admin)])

def make_slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "book"

@router.get("", response_model=BookList)
def admin_list_books(page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(Book)
    total = query.count()
    items = query.order_by(Book.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return BookList(items=items, total=total, page=page, page_size=page_size)

@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    slug = payload.slug or make_slug(payload.title)
    if db.query(Book).filter(Book.slug == slug).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    book = Book(**payload.model_dump(exclude={"slug"}), slug=slug)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
