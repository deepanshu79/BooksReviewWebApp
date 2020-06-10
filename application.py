import os
import json
import requests

from flask import jsonify
from flask import session
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Default route
@app.route("/")
def index():
    return render_template("index.html")
    

# Route to register
@app.route("/register", methods = ["GET", "POST"])
def register():
    # If method used to access route is 'GET'
    if request.method == "GET" :
        return render_template("register.html")
    # If method used to access route is 'POST'
    elif request.method == "POST" :
        name = request.form.get("name")
        users = db.execute("SELECT * FROM users WHERE username = :username", {"username": name}).fetchone()
        # If username isn't taken
        if users is None:
            password = request.form.get("password")
            cpassword = request.form.get("cpassword")
            # If passwords don't match 
            if password!=cpassword :
                return render_template("error.html", message = "Passwords don't match.", choice = 1)
            # If passwords match
            else :
                email = request.form.get("email")
                # If any of entered details is empty 
                if name=="" or password =="" or cpassword =="" or email =="" :
                    return render_template("error.html", message = "Incomplete details.", choice = 1)
                # If neither of entered details is empty
                else :
                    db.execute("INSERT INTO users (username,password,email) VALUES (:username, :password, :email)", {"username": name, "password": password, "email": email})
                    db.commit()
                    return render_template("message.html", message = "Congratulations you are registered.")      
        # If username is already taken
        else:
            return render_template("error.html", message = "Username not available , please choose another one.", choice = 1)


# Route to login
@app.route("/login", methods=["GET","POST"])
def login():
    # If method used to access route is 'GET'
    if request.method == "GET" :    
        # If user isn't logged in
        if session.get("user") is None :
            return render_template("login.html")  
        # If user is logged in already            
        else :    
            return render_template("dashboard.html", username = session["user"])
    # If method used to access route is 'POST'
    elif request.method == "POST" :
        name = request.form.get("name")
        password = request.form.get("password")
        users = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": name, "password": password}).fetchone()
        # If entered login details don't match with database
        if users is None :
            return render_template("error.html", message = "Invalid login.", choice = 3)
        # User is logged in
        else :
            session["user"] = name
            return render_template("dashboard.html", username = name)
        

# Route for logout
@app.route("/logout")
def logout():
    # User is logged out
    session.clear()
    return render_template("index.html")
        
        
# Route for search results of query
@app.route("/results", methods=["POST"])
def results():
    # If user isn't logged in
    if session.get("user") is None :
        return render_template("message.html", message = "Login required.")
    # If user is logged in
    else :
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
        users = db.execute("SELECT * FROM books WHERE isbn_no ILIKE :isbn AND title ILIKE :title AND author ILIKE :author", {"isbn": "%"+isbn+"%", "title": "%"+title+"%", "author": "%"+author+"%"}).fetchall()
        return render_template("display.html", users = users)
   
   
# Route for viewing book's review statistics and for review submission by the user
@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn): 
    # If user isn't logged in
    if session.get("user") is None :
        return render_template("message.html", message = "Login required.")
    # If User is logged in
    else :
        # Shows book's review statistics
        if request.method == "GET" :  
            details = requests.get("https://www.goodreads.com/book/review_counts.json" , params = {"key": "nOmqhRfV67pE8qDrzYMG0g", "isbns": isbn})
            data = details.json()
            list = data["books"][0]
            info = db.execute("SELECT * FROM books WHERE isbn_no = :isbn_no", {"isbn_no": isbn}).fetchone()
            reviews = db.execute("SELECT * FROM review WHERE isbn = :isbn_no", {"isbn_no": isbn}).fetchall()
            return render_template("review.html", list = list , info = info, reviews = reviews)
        # Submission of user review and refreshing of page
        elif request.method == "POST" :   
            username = session["user"]
            check = db.execute("SELECT * FROM review WHERE isbn = :isbn_no AND username = :user", {"isbn_no": isbn, "user": username}).fetchone()
            # If user hasn't submitted review previously for same book
            if check is None :
                rating = request.form.get("rating")
                review = request.form.get("review")
                db.execute("INSERT INTO review (isbn,username,rating,review) VALUES (:isbn_no, :user, :rating, :review)", {"isbn_no": isbn, "user": username, "rating": rating, "review": review})
                db.commit()
                details = requests.get("https://www.goodreads.com/book/review_counts.json" , params = {"key": "nOmqhRfV67pE8qDrzYMG0g", "isbns": isbn})
                data = details.json()
                list = data["books"][0]
                info = db.execute("SELECT * FROM books WHERE isbn_no = :isbn_no", {"isbn_no": isbn}).fetchone()
                reviews = db.execute("SELECT * FROM review WHERE isbn = :isbn_no", {"isbn_no": isbn}).fetchall()
                return render_template("review.html", list = list , info = info, reviews = reviews)
            # If user has already submitted review for that book before
            else :
                return render_template("error.html", message = "Cannot submit review for same book twice.", choice = 2)
                
                
# API route - Gives json response
@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn_no = :isbn_no", {"isbn_no": isbn}).fetchone()
    # If book for given isbn number doesn't exist in database
    if book is None :
        return jsonify({"error": "Book doesn't exist in databases"}), 404
    # If book exist in database then returning json response having details about that book
    else :
        title = book['title']
        author = book['author']
        year = int(book['publication_year'])
        details = requests.get("https://www.goodreads.com/book/review_counts.json" , params = {"key": "nOmqhRfV67pE8qDrzYMG0g", "isbns": isbn})  
        data = details.json()
        review = data["books"][0]["reviews_count"]
        rating = float(data["books"][0]["average_rating"])
        return jsonify({
               "title": title,
               "author": author,
               "year": year,
               "isbn": isbn,
               "review_count": review,
               "average_score": rating
            })
        