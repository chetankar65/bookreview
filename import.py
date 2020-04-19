import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
DB_URL = 'postgresql+psycopg2://tnomtgthouaruf:c699b4fe6ac3ad99f9989f50835d6faa4466811fc8a46ff421f1fb55d635d66f@ec2-34-197-212-240.compute-1.amazonaws.com:5432/d9k5abigv08a3r'

engine = create_engine(DB_URL)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    count = 0
    for isbn, title, author,year in reader:
        db.execute("INSERT INTO books (isbn, name, author, year) VALUES (:isbn, :name, :author, :year)",{"isbn": isbn, "name": title.upper(), "author":author.upper(), "year":int(year)})
        count += 1
        print(count)
    db.commit()

main()
