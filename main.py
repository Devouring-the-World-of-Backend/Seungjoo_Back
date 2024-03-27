from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str
    published_year: int

    @validator('published_year')
    def verify_year(cls, year):
        current_year = datetime.now().year
        if year > current_year:
            raise ValueError('Invalid published year')
        return year

DB = {}

@app.get("/")
def read_root():
    return {"Hello, Library!"}

@app.post("/books", response_model=Book)
def add_book(book: Book):
    if book.id in DB:
        raise HTTPException(status_code=400, detail="Book already exists")
    DB[book.id] = book
    return book


@app.get("/books")
def read_book_list():
    book_list = list(DB.values())
    return book_list


@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    if book_id not in DB:
        raise HTTPException(status_code=404, detail="Book not found")
    return DB[book_id]


@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    if book_id not in DB:
        raise HTTPException(status_code=404, detail="Book not found")
    DB[book_id] = book
    return DB[book_id]


@app.delete("/books/{item_id}")
def delete_book(book_id: int):
    if book_id not in DB:
        raise HTTPException(status_code=404, detail="Book not found")
    del DB[book_id]
    return f"Book {book_id} has been deleted."
