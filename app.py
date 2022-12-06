from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from dotenv import load_dotenv
from six.moves.urllib.parse import urlencode

import requests
import os
from functools import wraps

from models import Book, User, Bookshelf, Review
from extensions import db, migrate, oauth, auth0
import utils

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

# Configure Postgres database url for SQLAlchemy from environment variable
DATABASE_URI = os.environ['DATABASE_URL']
# Workaround for SQLAlchemy 1.4+ with Heroku
# See https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
# and https://github.com/sqlalchemy/sqlalchemy/commit/a9b068ae564e5e775e312373088545b75aeaa1b0#r48347973
# or https://stackoverflow.com/a/66775026/9343949
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy database
db.init_app(app)
# Initialize Alembic migrations
migrate.init_app(app, db)

# Initialize OAuth integration
oauth.init_app(app)


@app.route('/')
def main():

    shelves = Bookshelf.query.limit(4)
    """Homepage of the app that shows first 10 bookshelves"""
    return render_template('homepage.html', bookshelves=shelves)


"""AUTHENTICATION"""


def requires_auth(f):
    """Decorator for routes that should require authentication to view"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'id' not in session:
            # Redirect to Login page here
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/callback')
def callback_handling():
    """Auth0 Callback Handler after login"""
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo

    session['id'] = userinfo['sub']
    session['name'] = userinfo['name']
    session['picture'] = userinfo['picture']
    session['nickname'] = userinfo['nickname']

    if User.query.filter_by(user_id=userinfo['sub']).first() is None:
        return redirect(url_for('signup'))

    return redirect(url_for('profile'))


@app.route('/login')
def login():
    """Redirects to Auth0 interface for login, redirects to /callback route when finished"""
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external=True))


@app.route('/logout')
def logout():
    """Redirects to Auth0 login route"""
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('main', _external=True), 'client_id': os.environ['AUTH0_CLIENTID']}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/signup', methods=['POST', 'GET'])
@requires_auth
def signup():
    # TODO make this not work if you already exist
    if request.method == "POST":
        new_username = request.form.get('username', None)
        if new_username is not None:
            if User.query.filter_by(username=new_username).first() is not None:
                return render_template("signup.html", error=True)
            else:
                new_user = User(session['id'], new_username)
                if session['picture'] is not None:
                    new_user.picture = session['picture']
                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('profile'))

    return render_template("signup.html")


"""SEARCH"""


@app.route('/find_book_by_title', methods=['POST'])
def find_by_title():
    """Displays first 15 results with a cover image, isbn, and author"""
    if request.method == "POST":
        print(request.form)
        # Get title from form
        orig_title = request.form.get('search_query', None)
        if orig_title is None:
            # TODO Error Handling
            pass
        # Format title for use in OpenLibrary API
        title_query = orig_title.replace(" ", "+")
        print(title_query)
        # Use OpenLibrary Search API to get the matching works
        r = requests.get(f'http://openlibrary.org/search.json?title={title_query}')
        print(r.status_code)
        if r.status_code != 200:
            # TODO Error Handling
            pass
        j = r.json()

        num_results = len(j['docs'])

        results_to_show = []
        i = 0
        while len(results_to_show) < 15 and i < num_results:
            next_result = j['docs'][i]
            if 'cover_i' in next_result and 'author_name' in next_result and 'isbn' in next_result:
                print(next_result)
                id = next_result['key'].split("/")[2]
                cover_id = next_result['cover_i']
                title = next_result['title']
                author = next_result['author_name'][0]
                isbn = next_result['isbn'][0]

                if 'first_sentence' in next_result:
                    first_sentence = next_result['first_sentence']
                else:
                    first_sentence = None

                results_to_show.append({"work_id": id, "cover_id": cover_id, "title": title, "author": author, "first_sentence": first_sentence, "isbn": isbn})
            else:
                pass
            i += 1

        print(results_to_show)

        if 'id' in session:
            bookshelves = User.query.filter_by(user_id=session['id']).first().bookshelves
        else:
            bookshelves = None

        return render_template('book_search_results.html', results=results_to_show, query=orig_title, shelves=bookshelves)


@app.route('/find_bookshelf', methods=['POST'])
def find_bookshelf():
    """Finds first 10 matching bookshelves using full text search and LIKE"""
    if request.method == "POST":
        print(request.form)
        # Get name from form
        orig_name = request.form.get('search_query', None)
        print(orig_name)
        results = Bookshelf.query.filter(Bookshelf.title.match(f"'''{orig_name}'''")).limit(10)
        print(results)
        return render_template("bookshelf_search_results.html", shelves=results, query=orig_name)


"""VIEW OBJECTS"""


# show all bookshelves
@app.route('/bookshelves/', methods=['GET'])
def get_bookshelves():
    bookshelf = Bookshelf.query.all()
    return render_template('all_review.html' , bookshelves=bookshelf)


@app.route('/bookshelf/<bookshelf_id>', methods=['GET'])
def get_bookshelf(bookshelf_id):
    """Shows detailed information on a bookshelf with <bookshelf_id>"""
    # TODO Error handling if bookshelf doesnt exist
    bookshelf = Bookshelf.query.filter_by(id=bookshelf_id).first()
    return render_template('bookshelf.html', books=bookshelf.books, owner=bookshelf.owner, title=bookshelf.title, id=bookshelf.id)


@app.route('/book/<book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.filter_by(id=book_id)
    return book


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if "id" in session and user.user_id == session["id"]:
        return redirect(url_for("profile"))
    else:
        return render_template('user.html', user=user, bookshelves=user.bookshelves, reviews=user.reviews)


""" PROFILE """


@app.route('/profile')
@requires_auth
def profile():
    """Shows detailed information about signed in user"""
    curr_user = User.query.filter_by(user_id=session['id']).first()
    return render_template('profile.html', user=session, bookshelves=curr_user.bookshelves, username=curr_user.username)


@app.route('/add_bookshelf', methods=['POST'])
def add_bookshelf():
    """Adds a bookshelf with given name to the current user"""
    if request.method == "POST":
        name = request.form.get('name', None)
        if name is not None:
            curr_user = User.query.filter_by(user_id=session['id']).first()
            new_shelf = Bookshelf(curr_user)
            new_shelf.title = name
            db.session.add(new_shelf)
            db.session.commit()

    return redirect(url_for('profile'))


@app.route('/add_book_to_bookshelf', methods=['POST'])
def add_book_to_bookshelf():
    """Add book to specified bookshelf after querying OpenLibrary for book info"""
    if request.method == "POST":
        print(request.form)
        # Get title from form
        # TODO check for error in bookshelf id
        shelf_id = request.form.get('bookshelf_id', None)
        shelf = Bookshelf.query.filter_by(id=shelf_id).first()

        # TODO this should not be isbn, use work ID instead most likely
        isbn = request.form.get('isbn', None)
        new_book = Book.query.filter_by(isbn=isbn).first()
        if new_book is None:
            new_book = Book(isbn)
            # TODO Error check this openAPI request
            book_info = utils.get_book_info(isbn, isbn=True)
            new_book.title = book_info['title']
            new_book.author = book_info['author']
            new_book.cover_image_link = book_info['cover_id']

        shelf.books.append(new_book)
        db.session.add(shelf)
        db.session.commit()
        return jsonify(status="OK")

    return jsonify(status="error", message="clown moment"), 500


@app.route('/remove_book_from_bookshelf', methods=['POST'])
def remove_book_from_bookshelf():
    if request.method == "POST":
        shelf_id = request.form.get('bookshelf_id', None)
        book_id = request.form.get('book_id', None)
        if shelf_id is None or book_id is None:
            return jsonify(status="error", message="bad request"), 500
        shelf = Bookshelf.query.filter_by(id=shelf_id).first()
        book = Book.query.filter_by(id=book_id).first()
        shelf.books.remove(book)
        db.session.add(shelf)
        db.session.commit()
        return jsonify(status="OK"), 200
    return jsonify(status="error", message="clown moment"), 500


@app.route('/delete_bookshelf', methods=['POST'])
def delete_bookshelf():
    if request.method == "POST":
        shelf_id = request.form.get('id', None)
        print(shelf_id)
        shelf = Bookshelf.query.filter_by(id=shelf_id).first()
        for book in shelf.books:
            shelf.books.remove(book)
        db.session.delete(shelf)
        db.session.commit()
        return redirect(url_for("profile"))
    return jsonify(status="error", message="Request Failed"), 500


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html')


""" TESTING """


if __name__ == '__main__':
    app.run()
