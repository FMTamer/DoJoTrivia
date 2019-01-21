from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import random
from helpers import *

app = Flask(__name__)
db = SQL("sqlite:///dojo.db")

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Checks if the forms are filled out.
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation") or not request.form.get("emailaddress"):
            return apology("Make sure to fill in all fields!")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match!")

        # Executes database into result and hashes the password
        result = db.execute("INSERT INTO users (username, hash_password, email) VALUES(:username, :hash_password, :email)",
        username=request.form.get("username"), hash_password=pwd_context.hash(request.form.get("password")), email=request.form.get("emailaddress"))
        # Checks if username or email is already in the database
        if not result:
            return apology("Either username or email already taken!")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # ensure username exists and password is correct

        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash_password"]):
            return apology("Invalid username and/or password!")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_ID"]
        session['username'] = rows[0]['username']
        return redirect(url_for("personal"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Checks if the forms are filled out.
        if not request.form.get("username") or not request.form.get("password"):
            return apology("Make sure to fill in all fields!")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # ensure username exists and password is correct

        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash_password"]):
            return apology("Invalid username and or password!")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_ID"]
        session['username'] = rows[0]['username']
        return redirect(url_for("personal"))
    else:
        return redirect(url_for("/"))

@app.route("/logout", methods=["GET"])
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return render_template("logout.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")

@app.route("/about-us")
def aboutus():
    return render_template("about-us.html")

@app.route("/personal")
@login_required
def personal():
    return render_template("personal-page.html", username = session['username'], test = session)

@app.route("/createquiz")
@login_required
def createquiz():
    return render_template("createquiz.html")

@app.route("/creategame", methods=["GET", "POST"])
@login_required
def creategame():
    if request.method == "GET":
        return render_template("creategame.html")
    else:
        get_userID = db.execute("SELECT user_ID FROM users")
        create_room = db.execute("SELECT game_room FROM game")

        room_ID = random.randint(1,5000)
        if room_ID not in create_room:
            while room_ID in create_room:
                room_ID = random.randint(1,5000)
        db.execute("INSERT INTO game (player_ID1, score_P1, game_room, score_P2, time, won_by, player_ID2, completed) VALUES(':get_userID', 'NULL', ':room_ID', 'NULL', 'NULL', 'NULL', 'NULL', '0')",
            get_userID = get_userID[0]["user_ID"], room_ID = room_ID)
        return redirect(url_for("answer"))

@app.route("/joingame")
@login_required
def joingame():
    return render_template("joining.html")

@app.route("/makeq")
@login_required
def makeq():
    return render_template("makeq.html")

@app.route("/results")
@login_required
def results():
    return render_template("results.html")

@app.route("/answer")
@login_required
def answer():
    return render_template("answer.html")

### end of application.py