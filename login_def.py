import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_string = "postgresql://postgres:s123@localhost/books"
db = create_engine(db_string)


def loginuser():
    users = db.execute("SELECT * FROM Users WHERE id =:id",
                       {"id": username}).fetchall()
    for user in users:
        #print(f" Title: {book.title}, Author: {book.author}, Isbn: {book.isbn}, Year:{book.year}")
        print(f"title: {user.id}")

    return users


if __name__ == "__main__":
    loginuser()
