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
import smtplib
import os
import ssl

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

def send_contact_mail(email):
    """
    Sends email from contact form
    """

    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "dojopython.webik@gmail.com"
    receiver_email = email
    password = "webik2019_"
    message = """\
Subject: Thank you for the feedback!
Dear player,
Thank you for the feedback, it will be taken into consideration!
Sincerely,
The DoJoTrivia Team"""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def get_match_history(user):
    """
    Return user's match history
    """
    # check if user has finished matches
    match_history = db.execute("SELECT player_ID1, player_ID2, time, won_by FROM game WHERE completed == 1 AND (player_ID1 == :user_ID or player_ID2 == :user_ID) ORDER BY time DESC", user_ID = user)
    if match_history:

        # check for valid  matches
        matchlist = [x for x in match_history if x['player_ID2'] != 'NULL' and x['player_ID1'] != x['player_ID2']]
        match_history = []

        # insert time finished, result and opponent into list
        for x in matchlist:
            appendage = {}
            appendage['time'] = x['time'][5:-3]
            if x['player_ID1'] == user:
                appendage['opponent'] = db.execute("SELECT username FROM users WHERE user_ID = :opp_ID", opp_ID = x['player_ID2'])[0]['username']
            else:
                appendage['opponent'] = db.execute("SELECT username FROM users WHERE user_ID = :opp_ID", opp_ID = x['player_ID1'])[0]['username']
            if x['won_by'] == session['username']:
                appendage['win'] = 'Won'
            elif x['won_by'] == 'Draw':
                appendage['win'] = 'Draw'
            else:
                appendage['win'] = 'Lost'
            match_history.append(appendage)
    # prevent new users from causing errors
    match_history += ['', '', '', '']

    return match_history

def get_wlr(user_ID, username):
    """
    Returns a user's wins losses, draws and win/loss ratio.
    """
    wlr = [len(db.execute("SELECT player_ID1 from game WHERE won_by = :username", username = username)),
            len(db.execute("SELECT player_ID1 from game WHERE won_by != :username AND won_by != 'Draw' AND (player_ID1 = :user_ID or player_ID2 = :user_ID) AND completed = 1", username = username, user_ID = user_ID)),
            len(db.execute("SELECT player_ID1 from game WHERE won_by = 'Draw' AND (player_ID1 = :user_ID or player_ID2 = :user_ID) AND completed = 1", user_ID = user_ID))]
    if wlr[1] == 0:
        wlr.append(wlr[0]/1)
    else:
        wlr.append(wlr[0]/wlr[1])

    return wlr

def insert_quiz(quiz_title, question, cor_answer, w_answer1, w_answer2, w_answer3):
    """
    Inserts question and answers into database.
    """
    db.execute("INSERT INTO quizzes (quiz_title, question, cor_answer, w_answer1, w_answer2, w_answer3) VALUES (:quiz_title, :question, :cor_answer, :w_answer1, :w_answer2, :w_answer3)",
        quiz_title = quiz_title, question = question, cor_answer = cor_answer, w_answer1 = w_answer1, w_answer2 = w_answer2, w_answer3 = w_answer3)