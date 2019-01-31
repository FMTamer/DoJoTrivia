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
    Generate unique room
    """
    room_ID = random.randint(1000,9999)
    checked_room = check_room()

    # check if generated room exists
    if room_ID not in checked_room:
        while room_ID in checked_room:
            room_ID = random.randint(1000,9999)

    # insert player 1 into game
    db.execute("INSERT INTO game (player_ID1, score_P1, game_room, score_P2, time, won_by, player_ID2, completed) VALUES(':get_userID1', '0', ':room_ID', '0', 'NULL', 'NULL', 'NULL', '0')",
        get_userID1 = session["user_id"], room_ID = room_ID)

    return room_ID

def insquote(string):
    string = string.replace('&quot;', "'").replace('&#039;', "'").replace('&shy;', '').replace('&aring;','å').replace('&rsquo;', "'").replace('&eacute;', "é").replace('&LDQUO;', "'")
    return string.replace('&RDQUO;', "'").replace('&amp;', '&').replace("&Uuml", 'ü')

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
    password = "webik20182019"
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
    password = "webik20182019"
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


def get_quizzes():
    """
    Returns all options for quizzes, including random.
    """
    return ['Random']+list({x['quiz_title'] for x in db.execute("SELECT quiz_title FROM quizzes")})


def random_quiz(room_ID):
    """
    Creates random quiz
    """
    # retrieve questions and answers from api
    api_call = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results']
    quizzes = [x for x in api_call]
    for x in quizzes:
        del x['category'], x['type'], x['difficulty']

    # insert questions into database
    q_ID = 0
    for x in quizzes:
        question = insquote(x['question'])
        correct_answer = insquote(x['correct_answer'])
        wrong_answer = [insquote(y)for y in x['incorrect_answers']]


        db.execute("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer, q_number) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca, :q_ID)",
    room_ID = room_ID, wa1 = wrong_answer[0], wa2 = wrong_answer[1], wa3 = wrong_answer[2], ca = correct_answer, quest = question, q_ID = q_ID)
        q_ID += 1

def selected_quiz(option, room_ID):
    """"
    Insert a selected quiz into the database.
    """
    # retrieve questions and answeres from database
    sel_quiz = db.execute("SELECT question, cor_answer, w_answer1, w_answer2, w_answer3 FROM quizzes WHERE quiz_title = :q_title", q_title = option)

    # paris questions and answers with right game room
    q_ID = 0
    for x in sel_quiz:
        question = x['question']
        correct_answer = x['cor_answer']
        wrong_answer = [x['w_answer1'],  x['w_answer2'], x['w_answer3']]
        print(question, correct_answer, wrong_answer)

        db.execute("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer, q_number) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca, :q_ID)",
    room_ID = room_ID, wa1 = wrong_answer[0], wa2 = wrong_answer[1], wa3 = wrong_answer[2], ca = correct_answer, quest = question, q_ID = q_ID)
        q_ID += 1

def quiz_values(room_ID, question_num):
    """
    Returns a list with the question, correct answer and wrong answers.
    """
     # get question and answers from database
    quiz =  db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID and q_number = :q_number", room_ID = room_ID, q_number = question_num)[0]
    question = quiz['question']
    wrong_answers = [quiz['w_answer1'], quiz['w_answer2'], quiz['w_answer3']]
    cor_answer = quiz['cor_answer']


    # scramble answers
    tempanswers = wrong_answers
    tempanswers.append(cor_answer)
    rempos = list(range(0, 4))
    answers = {}
    while rempos:
        x = random.choice(rempos)
        answers[x] = random.choice(tempanswers)
        rempos.remove(x)
        tempanswers.remove(answers[x])

    return answers, cor_answer, question

def insert_p2(user_ID, room_ID):
    """
    Inserts player 2 into the appropiate room
    """
    sessions = db.execute("SELECT player_ID2 FROM game WHERE game_room = :room", room = room_ID)
    if sessions:
        # check if session is full
        print(sessions)
        sessions = sessions[0]['player_ID2']
        print(sessions, user_ID)
        if sessions != 'NULL' and sessions != user_ID:
            print('1st')
            return False
        else:
            db.execute("UPDATE game SET player_ID2 = :user_ID2 WHERE game_room = :room", user_ID2 = user_ID, room = room_ID)
            return True
    if not sessions:
        return False

def game_end(room):
    """
    Determines who won or if the game was a draw
    """
    # initialize queries
    score_P1 = int(db.execute("SELECT score_P1, score_P2 FROM game WHERE game_room == :room", room = room)[0]['score_P1'])
    score_P2 = int(db.execute("SELECT score_P1, score_P2 FROM game WHERE game_room == :room", room = room)[0]['score_P2'])
    select_ID = "SELECT player_ID1, player_ID2 FROM game WHERE game_room == :room"
    select_username = "SELECT username FROM users WHERE user_ID == :ID"

    # player 1 won
    if score_P1 > score_P2:
        playersID = db.execute(select_ID, room = room)
        winnerID = playersID[0]['player_ID1']
        other_player = playersID[0]['player_ID2']
        winner = db.execute(select_username, ID = winnerID)[0]['username']
        player1 = winner
        player2 = db.execute(select_username, ID = other_player)[0]['username']
        db.execute("UPDATE game SET won_by = :winner , completed = :completed WHERE game_room = :room", winner = winner, completed = 1, room = room)
        return ['p1', winner, player1, player2]

    # player 2 won
    elif score_P1 < score_P2:
        playersID = db.execute(select_ID, room = room)
        winnerID = playersID[0]['player_ID2']
        other_player = playersID[0]['player_ID1']
        winner = db.execute(select_username, ID = winnerID)[0]['username']
        player2 = winner
        player1 = db.execute(select_username, ID = other_player)[0]['username']
        db.execute("UPDATE game SET won_by = :winner , completed = :completed WHERE game_room = :room", winner = winner, completed = 1, room = room)
        return ['p2', winner, player1, player2]

    # draw
    else:
        db.execute("UPDATE game SET won_by = :winner, completed = :completed WHERE game_room = :room", winner = 'Draw', completed = 1, room = room)
        return 'Draw'

def wait_for_player(room):
    """
    Ensures players can't skip ahead of each other
    """

    # confirms answer in database
    db.execute("UPDATE game SET answered = answered + 1 WHERE game_room == :room_ID", room_ID = room)

    # check if other player has answered
    prev_answered = db.execute("SELECT total_answered FROM game WHERE game_room == :room_ID", room_ID = room)[0]['total_answered']
    while db.execute("SELECT answered FROM game WHERE game_room == :room_ID", room_ID = room)[0]['answered'] < prev_answered + 2 :
        wait()
    db.execute("UPDATE game SET total_answered = answered WHERE game_room = :room_ID", room_ID = room)

def update_score(user, room):
    """
    Updates the score of players
    """
    # add score to player 1
    if db.execute("SELECT player_ID1 FROM game WHERE game_room = :room_ID" , room_ID = room)[0]['player_ID1'] == user:
            db.execute("UPDATE game SET score_P1 = score_P1 + 1 WHERE game_room == :room_ID", room_ID = room)

    # add score to player 2
    elif db.execute("SELECT player_ID2 FROM game WHERE game_room = :room_ID" , room_ID = room)[0]['player_ID2'] == user:
        print(db.execute("SELECT player_ID2 FROM game WHERE game_room = :room_ID" , room_ID = room)[0]['player_ID2'] == user)
        db.execute("UPDATE game SET score_P2 = score_P2 + 1 WHERE game_room == :room_ID", room_ID = room)


def quiz_length(room):
    """
    Returns the length of a given room's quiz
    """
    return len(db.execute("SELECT * FROM questions WHERE game_room = :room_ID", room_ID = room))

def insert_time(room):
    """
    Inserts time quiz ended into database
    """
    time_stamp = get_timestamp()
    db.execute("UPDATE game SET time = :time_stamp WHERE game_room = :game_ID", time_stamp = time_stamp, game_ID = room)