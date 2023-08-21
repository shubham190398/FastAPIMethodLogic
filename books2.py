from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()


class Book:
    ID: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(title="id is not needed")
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=5, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1990)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "A new book",
                "author": "Coding with Apo",
                "description": "A good book",
                "rating": 4,
                "published_date": 2000
            }
        }


BOOKS = [
    Book(1, "Computer Science Pro", "Apocoder", "A very nice book!", 5, 2011),
    Book(2, "FastAPI course", "Apocoder", "A great book!", 5, 2012),
    Book(3, "Master Endpoints", "Apocoder", "An awesome book!", 5, 2013),
    Book(4, "Harry Potter 1", "J.K. Rowling", "Could be better", 2, 2011),
    Book(5, "Harry Potter 2", "Dan Brown", "Average", 3, 2012),
    Book(6, "Harry Potter 3", "Sam Bourne", "Very bad book", 1, 2011),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(status_code=404, detail="Item not Found")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []

    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)

    return books_to_return


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_book_by_published_date(published_date: int = Query(gt=1990)):
    books_to_return = []

    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


@app.put("/books/update-book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    was_updated = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = Book(**book.model_dump())
            was_updated = True

    if not was_updated:
        raise HTTPException(status_code=404, detail="Item not Found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    was_deleted = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            was_deleted = True
            break

    if not was_deleted:
        raise HTTPException(status_code=404, detail="Item not Found")


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

    return book
