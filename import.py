import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    try:
        f = open("books.csv")
        reader = csv.reader(f)
        for isbn, title, author, year in reader:
            db.execute("INSERT INTO books (isbn_no, title, author, publication_year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        db.commit()
        print("Files successfully added into the database")
    except:
        print("An exception occurred")

if __name__ == "__main__":
    main()

