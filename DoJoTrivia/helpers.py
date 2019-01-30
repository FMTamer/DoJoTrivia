from cs50 import SQL
import csv
import urllib.request
import sqlite3
from flask import redirect, render_template, request, session
from functools import wraps
import random
import requests
from pytrivia import *
import time
from time import sleep
import datetime
from passlib.apps import custom_app_context as pwd_context

db = SQL("sqlite:///dojo.db")


def apology(message):
    """Renders apology message on the apology.html website."""
    def escape(s):
        """ cccccc
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", " "), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", bottom=escape(message))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return apology("You have to be logged in to visit this page!")
        return f(*args, **kwargs)
    return decorated_function

def new_member():
    result = db.execute("INSERT INTO users (username, hash_password, email) VALUES(:username, :hash_password, :email)",
    username=request.form.get("username"), hash_password=pwd_context.hash(request.form.get("password")), email=request.form.get("emailaddress"))
    return result

def login_authentication():
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
    if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash_password"]):
        return False
    else:
        session["user_id"] = rows[0]["user_ID"]
        session['username'] = rows[0]['username']
        return True

def check_room():
    return db.execute("SELECT game_room FROM game")

def empty_room(room_ID):
    return db.execute("SELECT game_room FROM game WHERE completed == 0 and game_room == :room_ID", room_ID = room_ID)

def generate():
    """
    <wat doet deze functie>
    """
    room_ID = random.randint(1000,9999)
    checked_room = check_room()

    # duidelijk maken
    if room_ID not in checked_room:
        while room_ID in checked_room:
            room_ID = random.randint(1000,9999)

    db.execute("INSERT INTO game (player_ID1, score_P1, game_room, score_P2, time, won_by, player_ID2, completed) VALUES(':get_userID1', '0', ':room_ID', '0', 'NULL', 'NULL', 'NULL', '0')",
        get_userID1 = session["user_id"], room_ID = room_ID)

    return room_ID

def insquote(string):
    string = string.replace('&quot;', "'").replace('&#039;', "'").replace('&shy;', '').replace('&aring;','å').replace('&rsquo;', "'").replace('&eacute;', "é").replace('&LDQUO;', "'")
    return string.replace('&RDQUO;', "'").replace('&AMP;', '&')

def title_taken(title):
    if title in [y for x in [list(x.values()) for x in db.execute("SELECT quiz_title FROM quizzes")] for y in x]:
        return True
    return False

def get_timestamp():
	ts = time.time()
	return  str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

def wait():
    sleep(2)

def send_register_mail(email):
    """
    Sends email to newly registered user
    """
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "dojopython.webik@gmail.com"
    receiver_email = email
    password = "webik2019_"
    message = """\
Subject: Welcome to DoJoTrivia!
Welcome new player,
Thank you for registering, we at DoJoTrivia hope you have a great time testing your knowledge and challenging your friends!
Sincerely,
The DoJoTrivia Team"""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

