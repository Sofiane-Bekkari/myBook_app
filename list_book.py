import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_string = "postgresql://postgres:s123@localhost/books"
db = create_engine(db_string)


def myBooklist():
    books = db.execute("SELECT * FROM books_list").fetchall()
    for book in books:
        #print(f" Title: {book.title}, Author: {book.author}, Isbn: {book.isbn}, Year:{book.year}")
        return books


if __name__ == "__main__":
    myBooklist()
