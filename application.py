import csv
import os
import re
import requests
import hashlib
import jsonify

from flask import Flask, render_template, request, redirect, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
#postgresql+psycopg2://tnomtgthouaruf:c699b4fe6ac3ad99f9989f50835d6faa4466811fc8a46ff421f1fb55d635d66f@ec2-34-197-212-240.compute-1.amazonaws.com:5432/d9k5abigv08a3r

app = Flask(__name__)
app.secret_key = 'any random string'

# Check for environment variable

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


regex = '^[a-zA-Z0-9](_(?!(\.|_))|\.(?!(_|\.))|[a-zA-Z0-9]){6,18}[a-zA-Z0-9]$'

# Set up database
#os.getenv("DATABASE_URL")
engine = create_engine(os.getenv("DATABASE_URL")) #Postgres database URL hosted on heroku
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():      
    if session.get('user_id'):
        return redirect('/search')
    else:
        return render_template("index.html",message="Please fill out the details.", div = 'none')

@app.route('/register',methods=['POST'])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    newpass = password + "abmcnk2o210u9win" #salting
    password_hash = hashlib.md5(newpass.encode())
    if(re.search(regex,email)):
        if db.execute("SELECT * FROM users WHERE username = :email",{"email":email}).rowcount == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",{"username": email, "password": password_hash.hexdigest()})
            db.commit()
            return redirect("/login")
        else:
            message = 'User already exists'
            div = 'alert alert-warning'
            return render_template("index.html",message=message, div = div)
    else:
        message = 'Email is not valid'
        div = 'alert alert-danger'
        return render_template("index.html",message=message, div = div)


@app.route("/login")
def login():
    if session.get('user_id'):
        return redirect('/search')
    else:
        return render_template("login.html")

@app.route("/loggedIn",methods=['POST'])
def loggedIn():
    email = request.form.get("email")
    password = request.form.get("password")
    newpass = password + "abmcnk2o210u9win" #salting
    password_hash = hashlib.md5(newpass.encode())
    if db.execute("SELECT * FROM users WHERE username = :email",{"email":email}).rowcount == 0:
        message = "Account doesn't exist"
        div = 'alert alert-warning'
        return render_template("login.html",message = message, div = div)
    else:
        rows = db.execute("SELECT id,username,password FROM users WHERE username = :email",{"email":email}).fetchone()
        if (password_hash.hexdigest() == rows.password and email == rows.username):
            session["user_id"] = rows.id
            return redirect("/search")
        else:
            message = 'Something went wrong'
            div = 'alert alert-danger'
            return render_template("login.html",message = message, div = div)


@app.route("/search")
def search():
    #user_id = session.get('user_id')
    if session.get('user_id'):
        return render_template("search.html")
    else:
        return redirect('/login')

@app.route('/searchquery',methods=['POST'])
def searchquery():
    data = request.form.get("data").upper()
    dataConcat = "%" + data + "%"
    sql = "SELECT isbn,name,author,year FROM books WHERE name LIKE :data0 OR author LIKE :data1 OR isbn = :data2"
    rows = db.execute(sql,{'data0':dataConcat,'data1':dataConcat,'data2':data}).fetchall()
    return render_template("search.html", rows = rows)

@app.route("/details/<string:isbn>")
def bookdetails(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "HHsR6ZZZEh1ETgQkOULg", "isbns": isbn})
    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE user_id = :userid AND isbn = :isbn",{"userid":session.get('user_id'),'isbn':isbn})
    if session.get('user_id'):
        if (reviews.rowcount == 0):
            reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{'isbn':isbn}).fetchall()
            html = True
            return render_template("details.html", rows = rows, html = html, reviews = reviews, res = res.json())
        else:
            reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{'isbn':isbn}).fetchall()
            html = False
            return render_template("details.html", rows = rows, html = html, reviews = reviews, res = res.json())
    else:
        return redirect('/')

@app.route('/submitreview', methods=['POST'])
def submitreview():
    ratings = request.form.get('rating')
    text = request.form.get("text")
    book_reviewed = request.form['submit_btn']
    db.execute("INSERT INTO reviews (rating,text,user_id,isbn) VALUES (:rating, :text, :user_id, :isbn)",{"rating": ratings, 'text':text, 'user_id':session.get('user_id'),'isbn':book_reviewed})
    db.commit()
    return redirect(f'/details/{book_reviewed}')

@app.route("/api/<string:isbn>")
def api(isbn):
    #This is the review count and average score received on this website, not from goodreads.
    rows = db.execute("SELECT isbn,name,author,year FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
    rows1 = db.execute("SELECT count(*),avg(rating) FROM reviews WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
    if (len(rows) > 0):
        return {"title":rows[0].name,"author":rows[0].author,"year":rows[0].year,"isbn":rows[0].isbn,"review_count":str(rows1[0].count),"average_score":str(rows1[0].avg)}
    else:
        return "404 : Not found"
        
@app.route("/logout")
def logout():
    #select from database where book isbn = isbn.parameter
    session.pop('user_id', None)
    return redirect('/')
    

def hash(string):
    pass
