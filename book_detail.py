import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_string = "postgresql://postgres:s123@localhost/books"
db = create_engine(db_string)


def myBook_detail():
    book_id = int(request.form.get("book_id"))
    book = db.execute("SELECT * FROM books_list WHERE id = :id",
                      {"id": book_id}).fetchone()
    if book is None:
        flash('No sush a book')
        # return render_template("error.html", message="No such flight.")


if __name__ == "__main__":
    myBook_detail()
