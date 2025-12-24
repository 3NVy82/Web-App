from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import get_db

router = APIRouter(prefix="/books", tags=["books"])

# СОЗДАТЬ книгу
@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    # current_user будет позже, пока закомментируйте
    # current_user: schemas.UserResponse = Depends(get_current_user)
):
    # Временно используем первого пользователя
    first_user = db.query(models.User).first()
    if not first_user:
        # Создаем тестового пользователя
        from auth import get_password_hash
        first_user = models.User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_author=True
        )
        db.add(first_user)
        db.commit()
        db.refresh(first_user)
    
    db_book = models.Book(**book.dict(), author_id=first_user.id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# ПОЛУЧИТЬ все книги
@router.get("/", response_model=List[schemas.BookWithAuthor])
def get_books(
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Book)
    
    if genre:
        query = query.filter(models.Book.genre.ilike(f"%{genre}%"))
    
    books = query.offset(skip).limit(limit).all()
    return books

# ПОЛУЧИТЬ одну книгу
@router.get("/{book_id}", response_model=schemas.BookWithAuthor)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

# ОБНОВИТЬ книгу
@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book_update: schemas.BookCreate,
    db: Session = Depends(get_db)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    for key, value in book_update.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

# УДАЛИТЬ книгу
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    db.delete(db_book)
    db.commit()
    return None