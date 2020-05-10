import csv
import os

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_string = "postgresql://postgres:s123@localhost/books"
db = create_engine(db_string)

def main():
    b = open("books.csv")
    reader = csv.reader(b)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books_list (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book from {isbn} and {title} by {author} .")
    db.commit()


if __name__ == "__main__":
    main()
