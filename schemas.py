from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

# ========== USER SCHEMAS ==========
class UserBase(BaseModel):
    email: str
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_author: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ========== BOOK SCHEMAS ==========
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    author_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BookWithAuthor(BookResponse):
    author: UserResponse

# ========== REVIEW SCHEMAS ==========
class ReviewBase(BaseModel):
    content: str = Field(..., min_length=10, max_length=2000)
    rating: int = Field(..., ge=1, le=5)

class ReviewCreate(ReviewBase):
    book_id: int

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ReviewWithUser(ReviewResponse):
    user: UserResponse

class ReviewWithBook(ReviewResponse):
    book: BookResponse