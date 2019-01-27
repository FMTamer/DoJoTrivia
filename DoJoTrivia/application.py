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

            # api_call
            api_call = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results']

            quizzes = [x for x in api_call]
            for x in quizzes:
                del x['category'], x['type'], x['difficulty']



            print(quizzes)
            api_call = api_call[0]

            # store useable values
            quizlist = (insquote(api_call['question']), insquote(api_call['correct_answer']), [insquote(x) for x in api_call['incorrect_answers']])

            # store in database
            db.execute("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca)",
            room_ID = room_ID, wa1 = quizlist[2][0], wa2 = quizlist[2][1], wa3 = quizlist[2][2], ca = quizlist[1], quest = quizlist[0])

            # automatize
            loopyboi = 1
            for i in range(39):
                # set variable to add
                addable = ''
                x = str(i+2)
                if loopyboi % 5 == 1:
                    addable = x+'question'
                if loopyboi % 5 == 2:
                    addable = x+'w_answer1'
                if loopyboi % 5 == 3:
                    addable = x+'w_answer2'
                if loopyboi % 5 == 4:
                    addable = x+'w_answer3'
                else:
                    addable = x+'cor_answer'
                loopyboi += 1
                print(addable)
                # db.execute("ALTER TABLE questions ADD :q text",
                # q = i+'question',
                # wa1 = i +'w_answer1',
                # wa2 = i +'w_answer2',
                # wa3 = i +'w_answer3',
                # ca = i + 'cor_answer'
                # )

            # scramble answers
            tempanswers = quizlist[2]
            tempanswers.append(quizlist[1])
            rempos = list(range(0, 4))
            answers = {}
            while rempos:
                x = random.choice(rempos)
                answers[x] = random.choice(tempanswers)
                rempos.remove(x)
                tempanswers.remove(answers[x])

            # render sites
            return render_template("answer.html", room = session['room_ID'], test = loopyboi, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = quizlist[1], question = quizlist[0])
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
        print("KANKER")
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


