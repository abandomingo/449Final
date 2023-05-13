Hello this is our Final Project in CPSC 449
by Aban Domingo and Brandon Winkler

This project uses Fast API, Python, and MongoDB
in order to create an online bookstore that has information such as
Title, Author, Price, Stock, Sold and Summary

The following are test routes used to interact with the database
GET http://localhost:8000/books                                                 #Get all Books
GET http://localhost:8000/books-total                                           #Number of Books
GET http://localhost:8000/bestsellers                                           #Top 5 BestSellers
GET http://localhost:8000/most-books-in-store   #Get all Books                  #Top 5 Authors with Books in Store
GET http://localhost:8000/search?title={}&author={}&min_price={}&max_price={}   #Search for Book
GET http://localhost:8000/books/{book_id}                                       #Get Book by Id
POST http://localhost:8000/books                                                #Create A Book
PUT http://localhost:8000/books/{book_id}                                       #Update A Book
DELETE  http://localhost:8000/books/{book_id}                                   #Delete A Book
