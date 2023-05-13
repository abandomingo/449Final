from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List


app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["449_db"]


class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int
    sales: int
    
class UpdateBook(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    sold: Optional[int] = None

@app.get("/")
async def index():
    return {"message": "Hello World!"}

@app.get('/books')
async def get_books():
    # Retrieve all books from the "books" collection
    books = list(db.books.find())

    # Convert ObjectId objects to strings
    for book in books:
        book['_id'] = str(book['_id'])

    # Return the list of books
    return books

@app.get('/books')
async def get_books():
    # Retrieve all books from the "books" collection
    books = list(db.books.find())

    # Convert ObjectId objects to strings
    for book in books:
        book['_id'] = str(book['_id'])

    # Return the list of books
    return books

# Define the endpoint to retrieve a book by ID
@app.get('/books/{book_id}')
async def get_book_by_id(book_id: str):
    # Convert the book ID string to a MongoDB ObjectId object
    object_id = ObjectId(book_id)

    # Query the "books" collection for the book with the matching ID
    book = db.books.find_one({'_id': object_id})

    # Raise an HTTPException if the book is not found
    if not book:
        raise HTTPException(status_code=404, detail='Book not found')

    # Convert the ObjectId to a string for JSON serialization
    book['_id'] = str(book['_id'])

    # Return the book
    return book

# Define the endpoint to create a new book
@app.post('/books')
async def create_book(book: Book):
    # Convert the Pydantic model to a MongoDB document
    book_doc = book.dict()

    # Insert the new book document into the "books" collection
    result = db.books.insert_one(book_doc)

    # Get the newly inserted book's ID
    book_id = str(result.inserted_id)

    # Add the ID to the book document
    book_doc['_id'] = book_id

    # Return the new book as a response
    return book_doc

@app.put("/books/{book_id}")
async def update_book(book_id: str, book: UpdateBook):
    result = db.books.update_one({"_id": ObjectId(book_id)}, 
                                       {"$set": book.dict()})
    if result.modified_count == 1:
        return {"message": "Book updated successfully."}
    else:
        return {"message": "Book not found."}

@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    result = db.books.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully."}
    else:
        return {"message": "Book not found."}


@app.get("/search")
def search_books(title: Optional[str] = None, author: Optional[str] = None, 
                 min_price: Optional[float] = None, max_price: Optional[float] = None):
    search_criteria = {}
    if title:
        search_criteria['title'] = {'$regex': title, '$options': 'i'}
    if author:
        search_criteria['author'] = {'$regex': author, '$options': 'i'}
    if min_price is not None and max_price is not None:
        search_criteria['price'] = {'$gte': min_price, '$lte': max_price}
    
    books = []
    for book in db.books.find(search_criteria):
        book['_id'] = str(book['_id']) # convert ObjectId to string
        books.append(book)
    
    return books

@app.get("/books-total")
def get_books_total_stock():
    pipeline = [
        {"$project": {"_id": 0, "stock": 1}}
    ]

    result = list(db.books.aggregate(pipeline))

    total_stock = sum(book["stock"] for book in result)

    return {"total_stock": total_stock}

@app.get("/bestsellers")
def get_bestsellers():
    pipeline = [
        {"$sort": {"sales": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "title": 1, "sales": 1}}
    ]

    result = list(db.books.aggregate(pipeline))

    return {"bestsellers": result}

@app.get("/most-books-in-store")
def get_authors_most_stock():
    pipeline = [
        {"$group": {"_id": "$author", "total_stock": {"$sum": "$stock"}}},
        {"$sort": {"total_stock": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "author": "$_id", "total_stock": 1}}
    ]

    result = list(db.books.aggregate(pipeline))

    return {"authors_most_stock": result}
