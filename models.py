from extensions import db


class Book(db.Model):
    """
    Model to represent a book and its information
    """

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(), nullable=False)
    title = db.Column(db.String())
    author = db.Column(db.String())
    cover_image_link = db.Column(db.String())

    bookshelves = db.relationship('Bookshelf', secondary="savedBooks", back_populates="books")

    def __init__(self, isbn):
        self.isbn = isbn


class Bookshelf(db.Model):
    """
    Model to represent a users bookshelf with some number of books
    """
    __tablename__ = 'bookshelves'

    id = db.Column(db.Integer, primary_key=True)
    books = db.relationship('Book', secondary="savedBooks", back_populates='bookshelves')
    title = db.Column(db.String())
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('bookshelves', lazy=True))

    def __init__(self, owner):
        self.owner = owner


"""
A join table to map books to bookshelves
https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
https://fmhelp.filemaker.com/help/18/fmp/en/index.html#page/FMP_Help/many-to-many-relationships.html
"""
# TODO Ensure deletion works
# (https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table)
savedBooks = db.Table(
    'savedBooks',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('bookshelf_id', db.Integer, db.ForeignKey('bookshelves.id'), primary_key=True)
)


class User(db.Model):
    """
    Model to represent a user
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # The Auth0 'sub' field
    user_id = db.Column(db.String(), unique=True)
    picture = db.Column(db.String())
    username = db.Column(db.String(length=20), nullable=False, unique=True)

    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username


class Review(db.Model):
    """
    Model to represent a review of one book by one user
    """
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    # Rating from 1 - 5
    rating = db.Column(db.Integer)
    text_review = db.Column(db.String(length=200))

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    associated_book = db.relationship('Book', backref=db.backref('reviews', lazy=True))

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('reviews', lazy=True))

    def __init__(self, owner, associated_book):
        self.associated_book = associated_book
        self.owner = owner
