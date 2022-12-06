# Module 1 Group Assignment

CSCI 5117, Spring 2022, [assignment description](https://canvas.umn.edu/courses/291031/pages/project-1)

## App Info:

* Team Name: Goodreads 2
* App Name: Kallax
* App Link: http://kallax.me

### Students

* Ryan Alexander, alexa9070@umn.edu
* Junsoo Choi, choix712@umn.edu
* Dan Black, blac0352@umn.edu
* Pun Rojanavitsakul,rojan004@umn.edu


## Key Features

* Kallax uses the OpenLibrary Search API to back the search for individual book titles
* Kallax uses Ajax requests with JQuery to make adding books to bookshelves interactive without page reloads
* Kallax uses SQLAlchemy to easily perform full text search on bookshelf names

## Testing Notes

* Kallax uses SQLAlchemy as our ORM of choice. To setup a development database run `flask db migrate` to apply migrations.
* Please see the .env.example for other needed environment variables

## Screenshots of Site

![img](https://i.imgur.com/30F8Wt5.png)

This is the Kallax homepage that features a search bar and some user bookshelves

![img](https://i.imgur.com/jven7D3.png)

This is a user's profile page that has a form to create a new bookshelves and shows their current bookshelves

![img](https://i.imgur.com/zxGl8r6.png)

This is a bookshelf page where the user can edit the books on their shelf and delete it permanently.

![img](https://i.imgur.com/z7xvvZo.png)

This is the top of the search results page for the book "hobbit"

## Mock-up 

![home page and book page](assets/mockup1.jpg?raw=true "Home page and book page")
This is the mockup of the home page and book page
![user page and login page](assets/mockup2.jpg?raw=true "User page and login page")
This is the mockup of the user page and login page
![bookshelf page](assets/mockup3.jpg?raw=true "Bookshelf page")
This is the mockup of the bookshelf page


## External Dependencies

* SQLAlchemy: SQLAlchemy is an ORM we used to easily communicate with our database. Our DB models are defined in models.py and are queried from app.py
* Alembic: Alembic was used to apply migrations to our database in coordination with SQLAlchemy. Our migrations can be found migrations directory. More information can be found in the README in that directory.
* OpenLibrary API: We used OpenLibrary API to back our search for books. This was primarily accomplished by using their search API endpoint. After a user adds a search result we query their main API endpoint for a work to get information on author, title, and cover image. (https://openlibrary.org/dev/docs/api/search) and (https://openlibrary.org/dev/docs/api/books)
* python-dotenv: This library was used to handle loading the .env file more easily.
* Google Fonts: We used Google Fonts to import a custom font that better matched the theming of our website
* FontAwesome: We used FontAwesome primarily to add icons on different buttons throughout the app


