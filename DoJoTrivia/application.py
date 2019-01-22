from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import random
import smtplib
import os
import ssl
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
    if session:
        return render_template('personal-page.html')
    else:
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
    # forget any user_id
    session.clear()

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
        return redirect(url_for("personal", username = session['username']))
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
    else:
        if not request.form.get("username") or not request.form.get("emailaddress"):
            return apology("Make sure to fill in all fields!")
        else:
            port = 587
            smtp_server = "smtp.gmail.com"
            sender_email = "dojotrivia@gmail.com"
            receiver_email = request.form.get("emailaddress")
            password = "webik2019_"
            message = """\
            Subject: Thanks for the feedback!

    Thank you for your feedback, it will be taken into consideration!"""

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return apology("Thanks for the feedback!")



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
        generate()
        return redirect(url_for("answer"))

@app.route("/joingame",  methods=["GET", "POST"])
@login_required
def joingame():
    if request.method == "GET":
        return render_template("joining.html")
    else:
        given_room = [x for x in [a['game_room'] for a in check_room()] if x == int(request.form.get("room_num"))]
        kk =  '''UPDATE game SET player_ID2 = :user_ID2 WHERE game_room = :room '''
        if given_room:
            db.execute(kk, user_ID2 = get_userID(), room = given_room)
            return render_template('answer.html', test = given_room)
        else:
            return apology("This room numver does not exist")

        # given_room = int(request.form.get("room_num"))
        # rooms = check_room()
        # print(rooms)
        # if not any(d['game_room'] == given_room for d in rooms):
        #     db.execute("UPDATE game SET (player_ID2 = get_userID2) WHERE game_room = given_room VALUES(':get_userID2')",
        #         get_userID2 = get_userID() )
        #     return redirect(url_for("answer"))
        # else:
        #     return apology("This room number does not exist!")

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
