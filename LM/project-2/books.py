from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    published_date: int
    rating: int

    def __init__(self, id, title, author, description, published_date, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.published_date = published_date
        self.rating = rating


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on creation", default=None)
    title: str = Field(..., min_length=3, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=100)
    published_date: int = Field(..., ge=1, le=2025)
    rating: int = Field(..., ge=1, le=5)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A New Book",
                "author": "Oak Stronginthearm",
                "description": "A most excellent book!",
                "published_date": 2024,
                "rating": 5,
            }
        }
    }


BOOKS = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book!", 2021, 5),
    Book(2, "Title Two", "Author Two", "Description Two", 2022, 3),
    Book(3, "Title Three", "Author Three", "Description Three", 1980, 5),
    Book(4, "Title Four", "Author Four", "Description Four", 1935, 2),
    Book(5, "Title Five", "Author Five", "Description Five", 2025, 1),
    Book(6, "Title Six", "Author Two", "Description Six", 2021, 4),
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book


@app.get("/books/")
async def read_book_by_rating(book_rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/published/")
async def read_book_by_published_date(published_date: int):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.post("/create_book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.put("/books/update_book")
async def update_book(updated_book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == updated_book.id:
            BOOKS[i] = updated_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break
