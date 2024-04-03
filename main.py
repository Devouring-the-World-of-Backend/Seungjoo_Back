from fastapi import FastAPI, HTTPException
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://example-frontend.com",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["GET", "POST", "PUT", "DELETE"],
    allow_headers = ["*"],
)


class Book(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    published_year: int

    @validator('published_year')
    def verify_year(cls, year):
        current_year = datetime.now().year
        if year > current_year:
            raise ValueError('Invalid published year')
        return year

DB : Dict[int, Book] = {}

@app.get("/")
def read_root():
    return {"Hello, Library!"}


@app.post("/books", response_model=Book)
def add_book(book: Book):
    if book.id in DB:
        raise HTTPException(status_code=400, detail="Book already exists")
    DB[book.id] = book
    return book


@app.get("/books", response_model=List[Book])
def read_books(title: Optional[str] = None, author: Optional[str] = None, 
               published_year: Optional[int] = None):
    results = list(DB.values())
    if title:
        results = [book for book in results if title.lower() in book.title.lower()]
    if author:
        results = [book for book in results if author.lower() in book.author.lower()]
    if published_year:
        results = [book for book in results if published_year == book.published_year]
    return results


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


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id not in DB:
        raise HTTPException(status_code=404, detail="Book not found")
    del DB[book_id]
    return f"Book {book_id} has been deleted."


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message":exc.detail})


client = TestClient(app)


def test_create_book():
    new_book = {
        "id": 0,
        "title": "FastAPI 기초",
        "author": "한승주",
        "description": "test",
        "published_year": 2023
    }
    response = client.post("/books", json=new_book)
    assert response.status_code == 200

def test_create_book_fail():
    duplicated_book = {
        "id": 0,
        "title": "FastAPI 기초",
        "author": "한승주",
        "description": "test",
        "published_year": 2023
    }
    response = client.post("/books", json=duplicated_book)
    assert response.status_code == 400
    assert response.json() == {"message": "Book already exists"}

def test_read_book_list():
    response = client.get("/books")
    assert response.status_code == 200

def test_read_book():
    response = client.get("/books/0")
    assert response.status_code == 200

def test_read_book_fail():
    response = client.get("/books/10")
    assert response.status_code == 404
    assert response.json() == {"message": "Book not found"}

def test_update_book():
    update_book = {
        "id": 0,
        "title": "C언어 기초",
        "author": "한승주",
        "description": "test",
        "published_year": 2012
    }
    response = client.put("/books/0", json=update_book)
    assert response.status_code == 200

def test_update_book_fail():
    nonexistent_book = {
        "id": 100,
        "title": "C언어 기초",
        "author": "한승주",
        "description": "test",
        "published_year": 2012
    }
    response = client.put("/books/100", json=nonexistent_book)
    assert response.status_code == 404
    assert response.json() == {"message": "Book not found"}

def test_delete_book():
    response = client.delete("/books/0")
    assert response.status_code == 200

def test_delete_book_fail():
    response = client.delete("/books/100")
    assert response.status_code == 404
    assert response.json() == {"message": "Book not found"}