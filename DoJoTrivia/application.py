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



@app.route("/about-us")
def aboutus():
    return render_template("about-us.html")


@app.route("/personal")
@login_required
def personal():
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
            # question, correct answer, incorrect-answers 0-3
            # api_call
            api_call = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results']
            dictcall = [(insquote(x['question']), [str(insquote(a)) for a in x['incorrect_answers']], insquote(x['correct_answer'])) for x in api_call]
            # poep = {}
            # for i in range(len(dictcall)):
            #     poep[i] = dictcall[i]

            questdict = {x: dictcall[x][0] for x in range(len(dictcall))}
            wrong_answers = {x: dictcall[x][1] for x in range(len(dictcall))}
            coranswers = {x: dictcall[x][2] for x in range(len(dictcall))}


            # make json file
            jsonfile = {}
            for i in range(len(dictcall)) :
                jsonfile['q'+str(i)] = [dictcall[i][0], dictcall[i][1], dictcall[i][2]]
            jsonfile = json.dumps(jsonfile)


            # update database
            db.execute("INSERT INTO questions (game_room, JSON) VALUES(:room_ID, :api_call)", room_ID = room_ID, api_call = str(dictcall) )

            # temp question and answers
            test = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results'][0]
            question = insquote(test['question'])
            coranswer = insquote(test['correct_answer'])
            wrong = test['incorrect_answers']

            # creating answer list
            tempanswers = wrong
            tempanswers.append(coranswer)
            rempos = list(range(0, 4))
            answers = {}
            while rempos:
                x = random.choice(rempos)
                answers[x] = random.choice(tempanswers)
                rempos.remove(x)
                tempanswers.remove(answers[x])
            return render_template("answer.html", jsonfile = jsonfile, questdict=questdict, wrong_answers = wrong_answers, coranswers = coranswers, test = dictcall, question = question, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = coranswer)
        else:
            return apology("You are already in a game. Go continue with that bitch or leave the game.")


@app.route("/joingame",  methods=["GET", "POST"])
@login_required
def joingame():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM game WHERE completed == 0 and (player_ID1 == :userID or player_ID2 == :userID)", userID = get_userID())
        if len(rows) == 0:
            return render_template("joining.html")
        else:
            return apology("You are already in a game. Go continue with that bitch or leave the game.")
    else:
        given_room = [x for x in [a['game_room'] for a in check_room()] if x == int(request.form.get("room_num"))][0]
        if given_room:
            db.execute("UPDATE game SET player_ID2 = :user_ID2 WHERE game_room = :room", user_ID2 = get_userID(), room = given_room)
            return render_template('answer.html', room = given_room)
        else:
            return apology("This room number does not exist")

@app.route("/makeq")
@login_required
def makeq():
    return render_template("makeq.html")

@app.route("/results")
@login_required
def results():
    return render_template("results.html")

@app.route("/answer", methods=['GET', 'POST'])
@login_required
def answer():
    if request.method == 'GET':
        return render_template("answer.html", test = answers, question = question, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3],
        coranswer = coranswer)


@app.route('/correct_answer')
def background_process():
	try:
		score = request.args.get('scores', 0, type=str)
		if score == 1:
			return jsonify(result='You are wise')
		else:
			return jsonify(result='Try again.')
	except Exception as e:
		return str(e)

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
