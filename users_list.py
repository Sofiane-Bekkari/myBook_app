
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_string = "postgresql://postgres:s123@localhost/books"
db = create_engine(db_string)

#db_add = db
#db_add = SQLAlchemy(app)


def listUser():
    result = db.execute("SELECT * FROM users_list").fetchall()
    for u in result:
        #print(f"id: {book.id}, username: {book.username}, email {book.email} ")
        data = result
        return data


if __name__ == "__main__":
    listUser()
