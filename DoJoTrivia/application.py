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
from flask import jsonify
import requests
import json
import sqlite3


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

        port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = "dojotrivia@gmail.com"
        receiver_email = request.form.get("emailaddress")
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
    """
    Log user out.
    """

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
            return apology("Thanks for the feedback!")



@app.route("/about-us", methods = ['GET', 'POST'])
def aboutus():
    if request.method == 'GET':
        return render_template("about-us.html")
    else:
        db.execute("UPDATE game SET answered = answered + 1 WHERE completed == 0 AND game_room == :room_ID", room_ID = session['room_ID'])
        while db.execute("SELECT answered FROM game WHERE completed == 0 AND game_room == :room_ID", room_ID = session['room_ID'])[0]['answered'] < 2:
            wait()
        return render_template("results.html", answered = session['room_ID'])


@app.route("/personal")
@login_required
def personal():
    matches = db.execute("SELECT player_ID1, score_P1, game_room, score_P2, time, won_by, player_ID2 FROM game WHERE completed == 1 and (player_ID1 == :userID or player_ID2 == :userID)"
    , userID = session["user_id"] )
    print(matches)
    return render_template("personal-page.html", username = session['username'])

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
        # Create quiz
        #questions = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results']
        #question = questions[0]
        # Generate room with unique ID and Inserts it into DataBase of website.
        # rows = db.execute("SELECT * FROM game WHERE completed == 0 and (player_ID1 == :userID or player_ID2 == :userID)", userID = get_userID())
        rows = ''
        if len(rows) == 0:
            # Generates room code.
            room_ID = generate()
            session['room_ID'] = room_ID
            session['question_number'] = 0


            api_call = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results']

            quizzes = [x for x in api_call]
            for x in quizzes:
                del x['category'], x['type'], x['difficulty']

            # generate list of tuples to insert
            # allq = quizzes
            # sql_tups = [(x, room_ID, insquote(allq[x]['question']), insquote(allq[x]['correct_answer']), insquote(allq[x]['incorrect_answers'][0])
            # , insquote(allq[x]['incorrect_answers'][1]), insquote(allq[x]['incorrect_answers'][2])) for x in range(len(allq))]
            # inject = [(1, 2, 3, 4, 5, 6, 7), (1, 2, 3, 4,)]
            # print(sql_tups)
            # db.executemany("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer, q_number) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca, :q_ID)", inject)
            # room_ID = room_ID, wa1 = 2, wa2 = 2, wa3 = 2, ca =2, quest = 2, q_ID = 2)



            # enter questions into database
            q_ID = 0
            allq = quizzes
            for x in allq:
                question = insquote(x['question'])
                correct_answer = insquote(x['correct_answer'])
                wrong_answer = [insquote(y)for y in x['incorrect_answers']]


                db.execute("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer, q_number) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca, :q_ID)",
            room_ID = room_ID, wa1 = wrong_answer[0], wa2 = wrong_answer[1], wa3 = wrong_answer[2], ca = correct_answer, quest = question, q_ID = q_ID)
                q_ID += 1



            api_call = api_call[0]

            # store question in database
            quizlist = (insquote(api_call['question']), insquote(api_call['correct_answer']), [insquote(x) for x in api_call['incorrect_answers']])
            quiz =  db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID and q_number = :q_number", room_ID = room_ID, q_number = session['question_number'])
            question = quiz[0]['question']
            wrong_answers = [quiz[0]['w_answer1'], quiz[0]['w_answer2'], quiz[0]['w_answer3']]
            cor_answer = quiz[0]['cor_answer']
            print(question, wrong_answers, cor_answer)

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

            # render sites
            return render_template("answer.html", room = session['room_ID'], test = allq, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = quizlist[1], question = quizlist[0])
        else:
            return apology("You are already in a game. Go continue with that or leave the game.")


@app.route("/joingame",  methods=["GET", "POST"])
@login_required
def joingame():
    if request.method == "GET":
        # check if player is already in game
        # rows = db.execute("SELECT * FROM game WHERE completed == 0 and (player_ID1 == :userID or player_ID2 == :userID)", userID = get_userID())
        rows = ''
        if len(rows) == 0:
            return render_template("joining.html")
        else:
            return apology("You are already in a game. Go continue with that or leave the game.")

    else:
        # check if room number exits and assign to session
        session['room_ID'] = [x for x in [a['game_room'] for a in check_room()] if x == int(request.form.get("room_num"))][0]
        if session['room_ID']:
            # update database
            db.execute("UPDATE game SET player_ID2 = :user_ID2 WHERE game_room = :room", user_ID2 = get_userID(), room = session['room_ID'])


            # retrieve quiz from database
            quizlist = db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID", room_ID = session['room_ID'])
            question = quizlist[0]['question']
            wrong_answers = [quizlist[0]['w_answer1'], quizlist[0]['w_answer2'], quizlist[0]['w_answer3']]
            coranswer = quizlist[0]['cor_answer']

            # scramble answers
            tempanswers = wrong_answers
            tempanswers.append(coranswer)
            rempos = list(range(0, 4))
            answers = {}
            while rempos:
                x = random.choice(rempos)
                answers[x] = random.choice(tempanswers)
                rempos.remove(x)
                tempanswers.remove(answers[x])

            return render_template('answer.html', room = session['room_ID'], test = quizlist, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = coranswer, question = question)
        else:
            return apology("This room number does not exist")

@app.route("/makeq")
@login_required
def makeq():
    return render_template("makeq.html")

@app.route("/results", methods=["GET"])
@login_required
def ending_game():
    if request.method == "GET":
        time_stamp = get_timestamp()
        user_ID = get_userID()
        room = db.execute("SELECT game_room FROM game WHERE completed == 0 and (player_ID1 == :userID or player_ID2 == :userID)",
                userID = user_ID)
        room = room[0]['game_room']
        score_P1 = 8
        score_P2 = 4
        if score_P1 > score_P2:
            winnerID = db.execute("SELECT player_ID1 FROM game WHERE (completed == 0 and game_room == :room)", room = room)
            winnerID = winnerID[0]['player_ID1']
            winner = db.execute("SELECT username FROM users WHERE user_ID == :winnerID", winnerID = winnerID)
            winner = winner[0]['username']
        elif score_P1 < score_P2:
            winnerID = db.execute("SELECT player_ID2 FROM game WHERE (completed == 0 and game_room == :room)", room = room)
            winnerID = winnerID[0]['player_ID2']
            winner = db.execute("SELECT username FROM users WHERE user_ID == :winnerID", winnerID = winnerID)
            winner = winner[0]['username']
        else:
            db.execute("UPDATE game SET score_P1 = :score1, score_P2 = :score2, time = :time_stamp, won_by = player_ID2, completed = :completed WHERE game_room = :room",
                score1 = score_P1, score2 = score_P2, time_stamp = time_stamp, completed = 1, room = room)
            return render_template("results.html", room = room, time = time_stamp, score_P1 = score_P1, score_P2 = score_P2, winner = "Gelijkspel!")

        db.execute("UPDATE game SET score_P1 = :score1, score_P2 = :score2, time = :time_stamp, won_by = player_ID2, completed = :completed WHERE game_room = :room",
            score1 = score_P1, score2 = score_P2, time_stamp = time_stamp, completed = 1, room = room)

        return render_template("results.html", room = room, time = time_stamp, score_P1 = score_P1, score_P2 = score_P2, winner = winner)




@app.route("/answer", methods=['GET', 'POST'])
@login_required
def answer():
    if request.method == 'GET':
        return render_template("answer.html", test = answers, question = question, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3],
        coranswer = coranswer)

@app.route('/next_quiz', methods=['GET', 'POST'])
def background_process():
    return redirect(url_for("ending_game"))

@app.route("/retreat", methods=['POST'])
@login_required
def retreat():
    time_stamp = get_timestamp()
    user_ID = get_userID()
    room = db.execute("SELECT game_room FROM game WHERE completed == 0 and (player_ID1 == :userID or player_ID2 == :userID)",
            userID = user_ID)
    room = room[0]['game_room']

    check_ID = db.execute("SELECT player_ID1 FROM game WHERE game_room = :room",
            room = room)

    if user_ID in check_ID:
        db.execute("UPDATE game SET score_P1 = :score1, score_P2 = :score2, time = :time_stamp, won_by = player_ID2, completed = :completed WHERE game_room = :room",
            score1 = 0, score2 = 10, time_stamp = time_stamp, completed = 1, room = room)
    else:
        db.execute("UPDATE game SET score_P1 = :score1, score_P2 = :score2, time = :time_stamp, won_by = player_ID1, completed = :completed WHERE game_room = :room",
            score1 = 10, score2 = 0, time_stamp = time_stamp, completed = 1, room = room)
    return render_template("results.html")


