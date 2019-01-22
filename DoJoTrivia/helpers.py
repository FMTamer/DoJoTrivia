from cs50 import SQL
import csv
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps
import random

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

def get_userID():
    return session["user_id"]

def check_room():
    return db.execute("SELECT game_room FROM game")

def generate():
    room_ID = random.randint(1000,9999)
    checked_room = check_room()
    if room_ID not in checked_room:
        while room_ID in checked_room:
            room_ID = random.randint(1000,9999)
    db.execute("INSERT INTO game (player_ID1, score_P1, game_room, score_P2, time, won_by, player_ID2, completed) VALUES(':get_userID1', 'NULL', ':room_ID', 'NULL', 'NULL', 'NULL', 'NULL', '0')",
        get_userID1 = get_userID(), room_ID = room_ID)




