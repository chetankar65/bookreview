# Project 1

Web Programming with Python and JavaScript

This is a website where users can submit reviews for books and look at ratings.It has a massive catalog of books and uses GoodReads API to give user ratings and book details.

Here is a working link of the app hosted on heroku:---

The app uses the Flask microframework.
- Python for the backend scripting
- Postgres database engine
- HTML, CSS, Bootstrap ,JS and Jinja2 for dynamic layout.

The application.py contains server side code.
The index page contains registration form.
Login page contains login form.
Details page contains book details and search page contains search bar for books.

The database runs of PostgreSQL engine and the schema is:

USERS TABLE:
    - id serial primary key
    - Username varchar
    - Password varchar

BOOKS TABLE (IMPORTS FROM books.csv (import.py))
    - Id serial primary key
    - ISBN varchar
    - name varchar
    - author varchar
    - year integer

REVIEWS:
    - id serial primary key
    - user_id integer foreign key
    - rating integer
    - review text


