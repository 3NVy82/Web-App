from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])

# СОЗДАТЬ отзыв
@router.post("/", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли книга
    book = db.query(models.Book).filter(models.Book.id == review.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Берем первого пользователя
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users exist. Create a user first."
        )
    
    db_review = models.Review(
        **review.dict(),
        user_id=user.id
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

# ПОЛУЧИТЬ все отзывы
@router.get("/", response_model=List[schemas.ReviewWithUser])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    book_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Review)
    
    if book_id:
        query = query.filter(models.Review.book_id == book_id)
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews

# ПОЛУЧИТЬ отзывы для конкретной книги
@router.get("/book/{book_id}", response_model=List[schemas.ReviewWithUser])
def get_reviews_for_book(book_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.book_id == book_id).all()
    return reviews

# УДАЛИТЬ отзыв
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    db.delete(db_review)
    db.commit()
    return None