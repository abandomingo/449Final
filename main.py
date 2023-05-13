from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List


app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")  #localhost client
db = client["449_db"]                               #database


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
    try:
        # Retrieve all books from the "books" collection
        books = list(db.books.find())

        # Convert ObjectId objects to strings
        for book in books:
            book['_id'] = str(book['_id'])

        # Return the list of books
        return books

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

    except:
        # Handle any other exceptions
        raise HTTPException(status_code=400, detail='Bad Request')

@app.get('/books/{book_id}')
async def get_book_by_id(book_id: str):
    try:
        # Convert the book ID string to a MongoDB ObjectId object
        try:
            object_id = ObjectId(book_id)
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid book ID')

        # Query the "books" collection for the book with the matching ID
        book = db.books.find_one({'_id': object_id})

        # Raise an HTTPException if the book is not found
        if not book:
            raise HTTPException(status_code=404, detail='Book not found')

        # Convert the ObjectId to a string for JSON serialization
        book['_id'] = str(book['_id'])

        # Return the book
        return book

    except HTTPException:
        # Re-raise any HTTPException with the same status code and detail
        raise

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

    except:
        # Handle any other exceptions
        raise HTTPException(status_code=400, detail='Bad Request')

# Define the endpoint to create a new book

@app.post('/books')
async def create_book(book: Book):
    try:
        # Convert the Pydantic model to a MongoDB document
        book_doc = book.dict()

        # Insert the new book document into the "books" collection
        result = db.books.insert_one(book_doc)

        # Raise an HTTPException if the insertion was not successful
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail='Failed to create book')

        # Get the newly inserted book's ID
        book_id = str(result.inserted_id)

        # Add the ID to the book document
        book_doc['_id'] = book_id

        # Return the new book as a response
        return book_doc

    except HTTPException:
        # Re-raise any HTTPException with the same status code and detail
        raise

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

    except:
        # Handle any other exceptions
        raise HTTPException(status_code=400, detail='Bad Request')

@app.put("/books/{book_id}")
async def update_book(book_id: str, book: UpdateBook):
    try:
        # Convert the book ID string to a MongoDB ObjectId object
        try:
            object_id = ObjectId(book_id)
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid book ID')

        # Update the book in the "books" collection
        result = db.books.update_one({"_id": object_id}, {"$set": book.dict()})

        if result.modified_count == 1:
            return {"message": "Book updated successfully."}
        else:
            return {"message": "Book not found."}

    except HTTPException:
        # Re-raise any HTTPException with the same status code and detail
        raise

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

    except:
        # Handle any other exceptions
        raise HTTPException(status_code=400, detail='Bad Request')
    
@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    try:
        # Convert the book ID string to a MongoDB ObjectId object
        try:
            object_id = ObjectId(book_id)
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid book ID')

        # Delete the book from the "books" collection
        result = db.books.delete_one({"_id": object_id})

        if result.deleted_count == 1:
            return {"message": "Book deleted successfully."}
        else:
            return {"message": "Book not found."}

    except HTTPException:
        # Re-raise any HTTPException with the same status code and detail
        raise

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

    except:
        # Handle any other exceptions
        raise HTTPException(status_code=400, detail='Bad Request')


@app.get("/search")
def search_books(title: Optional[str] = None, author: Optional[str] = None,
                 min_price: Optional[float] = None, max_price: Optional[float] = None):
    try:
        search_criteria = {}
        if title:
            #use regex to find the title
            search_criteria['title'] = {'$regex': title, '$options': 'i'}
        if author:
            #use regex to find the author
            search_criteria['author'] = {'$regex': author, '$options': 'i'}
        if min_price is not None and max_price is not None:
            #Where price is greater than min_price and less than max_price
            search_criteria['price'] = {'$gte': min_price, '$lte': max_price}

        books = []
        for book in db.books.find(search_criteria):
            book['_id'] = str(book['_id']) # convert ObjectId to string
            books.append(book)

        return books

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

@app.get("/books-total")
def get_books_total_stock():
    try:
        pipeline = [
            {"$project": {"_id": 0, "stock": 1}}
        ]

        result = list(db.books.aggregate(pipeline))

        total_stock = sum(book.get("stock", 0) for book in result)

        return {"total_stock": total_stock}

    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

@app.get("/bestsellers")
def get_bestsellers():
    try:
        pipeline = [
            {"$sort": {"sales": -1}},
            {"$limit": 5},
            {"$project": {"_id": 0, "title": 1, "sales": 1}}
        ]

        result = list(db.books.aggregate(pipeline))

        return {"bestsellers": result}
    
    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')

@app.get("/most-books-in-store")
def get_authors_most_stock():
    try:
        pipeline = [
            {"$group": {"_id": "$author", "total_stock": {"$sum": "$stock"}}},
            {"$sort": {"total_stock": -1}},
            {"$limit": 5},
            {"$project": {"_id": 0, "author": "$_id", "total_stock": 1}}
        ]

        result = list(db.books.aggregate(pipeline))

        return {"authors_most_stock": result}
    
    except Exception as e:
        # Handle any unexpected exceptions
        raise HTTPException(status_code=500, detail='Internal Server Error')
