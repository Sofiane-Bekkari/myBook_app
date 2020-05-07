import os
import requests

from flask import Flask, render_template, redirect, request, session, logging, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, IntegerField, StringField, PasswordField, TextAreaField, validators, SelectField
from functools import wraps

# I do need to Uninstall Whooosh !!
from flask_whooshalchemy import StemmingAnalyzer

# Import Books list
from list_book import myBooklist
# Import Login
from users_list import listUser


app = Flask(__name__)


mybooks = myBooklist()
users = listUser()

print(users[1].password)


app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:s123@localhost/books'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_INDEX_PATH'] = 'whoosh'


# db_string = "postgresql://postgres:s123@localhost/books"
# db = create_engine(db_string, echo=True)
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


db = SQLAlchemy(app)


# Create a Reviews Table on DataBase
class Reviews(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String())
    username = db.Column(db.String())
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, isbn, username, rating, comments):
        self.isbn = isbn
        self.username = username
        self.rating = rating
        self.comments = comments


# Create a Users_list Table on DataBase
class Users_list(db.Model):
    __tablename__ = 'users_list'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, username, password):
        self.username = username
        self.password = password


# Create a Books list Table
class Books(db.Model):
    __searchable__ = ['isbn', 'title', 'author']
    __tablename__ = 'books_list'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String())
    title = db.Column(db.String(200))
    author = db.Column(db.String(200))
    year = db.Column(db.String(100))

    def __init__(self, isbn, title, author, year):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year


# Index page
@app.route('/')
def index():
    return render_template('home.html')

# Home page
@app.route('/home')
def home():
    return render_template('home.html')


# Book ID
@app.route('/book/<string:id>', methods=['GET', 'POST'])
def book(id):

    result = db.session.query(Books).get(id)
    isbn = result.isbn

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "dzWENhPvO5Oue29Pu7g", "isbns": isbn})
    api = res.json()

    # Access to value
    text = api["books"][0]["text_reviews_count"]
    rating = api["books"][0]["work_ratings_count"]
    average = api["books"][0]["average_rating"]

    # Get Rating and Comments
    try:
        if request.method == 'POST':

            username = session['user_username']
            P_rating = request.form['rating']
            P_comment = request.form['comments']

            # Add and Check if the same user add rate or comment
            if db.session.query(Reviews).filter(Reviews.username == username).count() == 0 or db.session.query(Reviews).filter(Reviews.isbn == isbn).count() == 0:
                data = Reviews(isbn, username, P_rating, P_comment)
                db.session.add(data)
                db.session.commit()
                flash('You Are Submit a Review', 'success')
                return render_template("book.html", result=result, rating=rating, average=average, text=text)

            # If Submit already
            flash('You Already Submit a Review for this Book', 'danger')
            return render_template("book.html", result=result, rating=rating, average=average, text=text)
    except KeyError:
        flash('Please Rate or Comment before you submit!', 'warning')

    return render_template("book.html", result=result, rating=rating, average=average, text=text)


# Register Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=5, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])

# Serching Class


class BookSearchForm(Form):
    choices = [('isbn', 'Isbn'),
               ('title', 'Title'),
               ('author', 'Author')]
    select = SelectField('Select option:', choices=choices)
    search = StringField('Enter your search')


# Registeration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    # Here data from USER!
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        # For our DATABASE
        if db.session.query(Users_list).filter(Users_list.username == username).count() == 0:
            data = Users_list(username, password)
            db.session.add(data)
            db.session.commit()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
        flash('You already have a account', 'danger')

    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        users = listUser()
        username = request.form['username']
        password = request.form['password']

        # Get form information.
        if username == '' and password == '':
            flash('Please fill in the Username and Password', 'warning')
            return render_template('login.html')
        try:
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                session['user_username'] = user.username
                session['logged_in'] = True
                flash('You are now logged in', 'success')
                return redirect(url_for('search'))
        except IndexError:
            flash('Invalid login', 'danger')
            return render_template("login.html")

    return render_template('login.html')


# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['logged_in'] == True:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# logout
@app.route('/logout')
def logout():
    session.clear()
    session['logged_in'] = False
    flash('You are logged out', 'success')
    return redirect(url_for('login'))


# Search Page
@app.route('/search', methods=['GET', 'POST'])
@is_logged_in
def search():
    search = BookSearchForm(request.form)
    select = BookSearchForm(request.form)

    if request.method == 'POST':
        return search_results(search, select)

    return render_template('search.html', form=search)

# Result Page
@app.route('/result')
def search_results(search, select):

    isbn = []
    titles = []
    authors = []

    search.string = search.data['search']
    select.string = select.data['select']

    # Catch search with ISBN
    if search.data['search'] != '' and select.data['select'] == 'isbn':
        qry = db.session.query(Books).filter(
            Books.isbn.like("%" + search.data['search'] + "%"))
        isbn = qry
        return render_template('result.html', isbn=isbn)

    # Catch search with TITLE
    elif search.data['search'] != '' and select.data['select'] == 'title':
        qry = db.session.query(Books).filter(
            Books.title.like("%" + search.data['search'] + "%"))
        titles = qry
        return render_template('result.html', titles=titles)

    # Catch search with AUTHOR
    elif search.data['search'] != '' and select.data['select'] == 'author':
        qry = db.session.query(Books).filter(
            Books.title.like("%" + search.data['search'] + "%"))
        authors = qry
        return render_template('result.html', authors=authors)

    if not isbn or titles or authors:
        flash('Type a keyword in search bar!', 'warning')
        return redirect('/search')

    else:
        # display no
        flash('No Result Found!', 'danger')
        return render_template('search.html')


@app.route("/api/book/<string:id>")
def book_api(id):
    # Return details about a single book

    # Make sure book are exists.
    result = db.session.query(Books).get(id)

    if result is None:
        return jsonify({"error": "Invalid id"}), 404

    # Get rating and comment
    review = db.session.query(Reviews).all()

    # Get reviews.
    rating = review
    rate = []
    text = []
    text_count = 0
    for r in rating:
        rate.append(r.rating)
        print(len(rate))
        text.append(r.comments)
    rate = len(rate)
    print(rate)
    # print(text)
    text_count = text.count(r.comments)
    return jsonify({
        "title": result.title,
        "author": result.author,
        "year": result.year,
        "isbn": result.isbn,
        "review_count": rate,
        "text_count": text_count,
    })


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()
