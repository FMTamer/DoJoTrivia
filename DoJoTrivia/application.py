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

        # Checks if username or email is already in the database
        if not new_member():
            return apology("Username or email already taken!")

        if login_authentication() == False:
            return apology("Invalid username and/or password!")

        # send_register_mail(request.form.get("emailaddress"))

        return redirect(url_for("personal"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # forget any user_id
    session.clear()

    if request.method == "POST":
        # Checks if the forms are filled out.
        if not request.form.get("username") or not request.form.get("password"):
            return apology("Make sure to fill in all fields!")

        if login_authentication() == False:
            return apology("Invalid username or password!")

        return redirect(url_for("personal", username = session['username']))
    else:
        return redirect(url_for("/"))

@app.route("/logout", methods=["GET"])
def logout():
    """
    Log user out.
    """

    # forgets all the sessions
    session.clear()

    # redirect user to login form
    return render_template("logout.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")
    else:
        port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = "dojopython.webik@gmail.com"
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
        return render_template("contacted.html")



@app.route("/about-us")
def aboutus():
    return render_template("about-us.html")

@app.route("/personal")
@login_required
def personal():
    # create match history
    match_history = db.execute("SELECT player_ID1, player_ID2, time, won_by FROM game WHERE completed == 1 AND (player_ID1 == :user_ID or player_ID2 == :user_ID) ORDER BY time DESC", user_ID = session['user_id'])
    print(match_history)
    if match_history:
        matchlist = [x for x in match_history if x['player_ID2'] != 'NULL' and x['player_ID1'] != x['player_ID2']]
        match_history = []
        for x in matchlist:
            appendage = {}
            appendage['time'] = x['time'][5:-3]
            if x['player_ID1'] == session['user_id']:
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
    match_history += ['', '', '', '']

    # get wins, losses and ratio
    wlr = [len(db.execute("SELECT player_ID1 from game WHERE won_by = :username", username = session['username'])),
        len(db.execute("SELECT player_ID1 from game WHERE won_by != :username AND won_by != 'Draw' AND (player_ID1 = :user_ID or player_ID2 = :user_ID) AND completed = 1", username = session['username'], user_ID = session['user_id'])),
        len(db.execute("SELECT player_ID1 from game WHERE won_by = 'Draw' AND (player_ID1 = :user_ID or player_ID2 = :user_ID) AND completed = 1", user_ID = session['user_id']))]
    print(wlr)
    if wlr[1] == 0:
        wlr.append(wlr[0]/1)
    else:
        wlr.append(wlr[0]/wlr[1])

    if wlr and match_history:
        return render_template("personal-page.html", username = session['username'], match_history = match_history, wlr = wlr)
    print('not sessions')
    wlr = [0, 0, 0]
    return render_template("personal-page.html", username = session['username'])


@app.route("/customquiz", methods = ['GET', 'POST'])
@login_required
def customquiz():
    if request.method == 'GET':
        return render_template("customquiz_title.html")

    session['quiz'] = request.form.get("quiztitle")
    if session['quiz']:
        if title_taken(session['quiz']) == True:
            return apology("That title is already taken")

        return redirect(url_for("custom_question"))

    return apology("You did not give a title!")


@app.route("/custom_question", methods = ['GET', 'POST'])
@login_required
def custom_question():
    if request.method ==  'GET':
        return render_template("custom_question.html", test = 1, test2 = session['quiz'])

    # get question and answers
    quiz_title = session['quiz']
    question = request.form.get("question")
    cor_answer = request.form.get("cor_answer")
    w_answer1 = request.form.get("w_answer1")
    w_answer2 = request.form.get("w_answer2")
    w_answer3 = request.form.get("w_answer3")
    if not any([question, cor_answer, w_answer1, w_answer2, w_answer3]):
        return apology("Please fill in all fields")

    # insert question into database
    db.execute("INSERT INTO quizzes (quiz_title, question, cor_answer, w_answer1, w_answer2, w_answer3) VALUES (:quiz_title, :question, :cor_answer, :w_answer1, :w_answer2, :w_answer3)",
    quiz_title = quiz_title, question = question, cor_answer = cor_answer, w_answer1 = w_answer1, w_answer2 = w_answer2, w_answer3 = w_answer3)


    return render_template("custom_question.html", test = [question, cor_answer, w_answer1, w_answer2, w_answer3], test2 = session['quiz'])


@app.route("/creategame", methods=["GET", "POST"])
@login_required
def creategame():
    if request.method == "GET":

        # create options for quizzes
        options = ['Random']+list({x['quiz_title'] for x in db.execute("SELECT quiz_title FROM quizzes")})

        return render_template("creategame.html", options = options, test3 = json.dumps(options), variable = 3)

    # Create quiz
    rows = ''
    if len(rows) == 0:
        # ensure both ways to get to this page work
        option = request.form.get("option")
        if option:
            option = option[1:-1]
        else:
            option = 'Random'
            print('--------------------')

        # Generates room code.
        room_ID = generate()
        session['room_ID'] = room_ID
        session['question_number'] = 0

        # get random quiz
        quizzes = []
        if option == 'Random':
            api_call = requests.get('https://opentdb.com/api.php?amount=10&type=multiple').json()['results']
            quizzes = [x for x in api_call]
            for x in quizzes:
                del x['category'], x['type'], x['difficulty']

            q_ID = 0
            for x in quizzes:
                question = insquote(x['question'])
                correct_answer = insquote(x['correct_answer'])
                wrong_answer = [insquote(y)for y in x['incorrect_answers']]


                db.execute("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer, q_number) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca, :q_ID)",
            room_ID = room_ID, wa1 = wrong_answer[0], wa2 = wrong_answer[1], wa3 = wrong_answer[2], ca = correct_answer, quest = question, q_ID = q_ID)
                q_ID += 1


        # get selected quiz
        else:
            sel_quiz = db.execute("SELECT question, cor_answer, w_answer1, w_answer2, w_answer3 FROM quizzes WHERE quiz_title = :q_title", q_title = option)
            print(sel_quiz)
            q_ID = 0
            for x in sel_quiz:
                question = x['question']
                correct_answer = x['cor_answer']
                wrong_answer = [x['w_answer1'],  x['w_answer2'], x['w_answer3']]
                print(question, correct_answer, wrong_answer)

                db.execute("INSERT INTO questions (game_room, question, w_answer1, w_answer2, w_answer3, cor_answer, q_number) VALUES(:room_ID, :quest, :wa1, :wa2, :wa3, :ca, :q_ID)",
            room_ID = room_ID, wa1 = wrong_answer[0], wa2 = wrong_answer[1], wa3 = wrong_answer[2], ca = correct_answer, quest = question, q_ID = q_ID)
                q_ID += 1





        # get question and answers from database
        quiz =  db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID and q_number = :q_number", room_ID = room_ID, q_number = session['question_number'])[0]
        question = quiz['question']
        wrong_answers = [quiz['w_answer1'], quiz['w_answer2'], quiz['w_answer3']]
        cor_answer = quiz['cor_answer']
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
        return render_template("answer.html", room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question,  option = option)
    else:
        return apology("You are already in a game. Go continue with that or leave the game.")


@app.route("/joingame",  methods=["GET", "POST"])
@login_required
def joingame():
    if request.method == "GET":
        # check if player is already in game
        # rows = db.execute("SELECT * FROM game WHERE completed == 0 and (player_ID1 == :userID or player_ID2 == :userID)", userID = session["user_id"])
        rows = ''
        if len(rows) == 0:
            return render_template("joining.html")
        else:
            return apology("You are already in a game. Go continue with that or leave the game.")

    else:
        # check if room number exits and assign to session
        if not empty_room(int(request.form.get("room_num"))):
            return apology("This room number is invalid!")
        session['room_ID'] = int(request.form.get("room_num"))
        room_ID = session['room_ID']

        session['question_number'] = 0
        db.execute("UPDATE game SET player_ID2 = :user_ID2 WHERE game_room = :room", user_ID2 = session["user_id"], room = session['room_ID'])


        # get question and answers from database
        quiz =  db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID and q_number = :q_number", room_ID = room_ID, q_number = session['question_number'])[0]
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

        return render_template('answer.html', room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question)

# @app.route("/makeq")
# @login_required
# def makeq():
#       return render_template("makeq.html")

@app.route("/results")
@login_required
def ending_game():
    user_ID = session["user_id"]
    room = session['room_ID']
    wait()
    game_info = db.execute("SELECT time, score_P1, score_P2 FROM game WHERE game_room == :room", room = room)
    time_stamp = game_info[0]['time']
    score_P1 = game_info[0]['score_P1']
    score_P2 = game_info[0]['score_P2']
    score_P1 = int(score_P1)
    score_P2 = int(score_P2)

    if score_P1 > score_P2:
        playersID = db.execute("SELECT player_ID1, player_ID2 FROM game WHERE game_room == :room", room = room)
        winnerID = playersID[0]['player_ID1']
        other_player = playersID[0]['player_ID2']

        winner = db.execute("SELECT username FROM users WHERE user_ID == :winnerID", winnerID = winnerID)
        winner = winner[0]['username']
        player1 = winner

        player2 = db.execute("SELECT username FROM users WHERE user_ID == :other_player", other_player = other_player)
        player2 = player2[0]['username']

    elif score_P1 < score_P2:
        playersID = db.execute("SELECT player_ID1, player_ID2 FROM game WHERE game_room == :room", room = room)
        winnerID = playersID[0]['player_ID2']
        other_player = playersID[0]['player_ID1']

        winner = db.execute("SELECT username FROM users WHERE user_ID == :winnerID", winnerID = winnerID)
        winner = winner[0]['username']
        player2 = winner

        player1 = db.execute("SELECT username FROM users WHERE user_ID == :other_player", other_player = other_player)
        player1 = player1[0]['username']
    else:
        db.execute("UPDATE game SET won_by = :winner, completed = :completed WHERE game_room = :room", winner = 'Draw', completed = 1, room = room)
        return render_template("results.html", room = room, time = time_stamp, score_P1 = score_P1, score_P2 = score_P2, winner = "Draw")

    db.execute("UPDATE game SET won_by = :winner , completed = :completed WHERE game_room = :room", winner = winner, completed = 1, room = room)
    return render_template("results.html", room = room, time = time_stamp, score_P1 = score_P1, score_P2 = score_P2, winner = winner, username1 = player1 , username2 = player2)



@app.route("/answer", methods=['GET', 'POST'])
@login_required
def answer():
    if request.method == 'GET':
        return render_template("answer.html", test = answers, question = question, answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3],
        coranswer = coranswer)

@app.route('/quizC', methods=['GET', 'POST'])
def correct_answer():
    # wait for other player
    prev_answered = db.execute("SELECT total_answered FROM game WHERE game_room == :room_ID", room_ID = session['room_ID'])[0]['total_answered']
    db.execute("UPDATE game SET answered = answered + 1 WHERE game_room == :room_ID", room_ID = session['room_ID'])
    p_answered = db.execute("SELECT answered FROM game WHERE game_room == :room_ID", room_ID = session['room_ID'])[0]['answered']
    while db.execute("SELECT answered FROM game WHERE game_room == :room_ID", room_ID = session['room_ID'])[0]['answered'] < prev_answered + 2 :
        wait()
    db.execute("UPDATE game SET total_answered = answered WHERE game_room = :room_ID", room_ID = session['room_ID'])


    # update right scores
    if db.execute("SELECT player_ID1 FROM game WHERE game_room = :room_ID" , room_ID = session["room_ID"])[0]['player_ID1'] == session['user_id']:
        db.execute("UPDATE game SET score_P1 = score_P1 + 1 WHERE game_room == :room_ID", room_ID = session['room_ID'])
        print('poep')
    elif db.execute("SELECT player_ID2 FROM game WHERE game_room = :room_ID" , room_ID = session["room_ID"])[0]['player_ID2'] == session['user_id']:
        print(db.execute("SELECT player_ID2 FROM game WHERE game_room = :room_ID" , room_ID = session["room_ID"])[0]['player_ID2'] == session['user_id'])
        db.execute("UPDATE game SET score_P2 = score_P2 + 1 WHERE game_room == :room_ID", room_ID = session['room_ID'])
        print('kech')

    # check if questions are left
    session['question_number'] += 1
    room_ID = session['room_ID']
    if session['question_number'] < len(db.execute("SELECT * FROM questions WHERE game_room = :room_ID", room_ID = room_ID)):
        question_number = session['question_number']


        # get question and answers from database
        quiz =  db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID and q_number = :q_number", room_ID = room_ID, q_number = session['question_number'])[0]
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

        return render_template('answer.html', room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question)

    time_stamp = get_timestamp()
    db.execute("UPDATE game SET time = :time_stamp", time_stamp = time_stamp)
    return redirect(url_for("ending_game"))

@app.route('/quizW', methods=['GET', 'POST'])
def wrong_answer():
    # wait for other player
    prev_answered = db.execute("SELECT total_answered FROM game WHERE game_room == :room_ID", room_ID = session['room_ID'])[0]['total_answered']
    db.execute("UPDATE game SET answered = answered + 1 WHERE game_room == :room_ID", room_ID = session['room_ID'])
    p_answered = db.execute("SELECT answered FROM game WHERE game_room == :room_ID", room_ID = session['room_ID'])[0]['answered']
    while db.execute("SELECT answered FROM game WHERE game_room == :room_ID", room_ID = session['room_ID'])[0]['answered'] < prev_answered + 2 :
        wait()
    db.execute("UPDATE game SET total_answered = answered WHERE game_room = :room_ID", room_ID = session['room_ID'])


    session['question_number'] += 1
    room_ID = session['room_ID']
    if session['question_number'] < len(db.execute("SELECT * FROM questions WHERE game_room = :room_ID", room_ID = room_ID)):
        question_number = session['question_number']


        # get question and answers from database
        quiz =  db.execute("SELECT question, w_answer1, w_answer2, w_answer3, cor_answer FROM questions WHERE game_room = :room_ID and q_number = :q_number", room_ID = room_ID, q_number = session['question_number'])[0]
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

        return render_template('answer.html', room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question)

    time_stamp = get_timestamp()
    db.execute("UPDATE game SET time = :time_stamp", time_stamp = time_stamp)
    return redirect(url_for("ending_game"))

@app.route("/retreat", methods=['POST'])
@login_required
def retreat():
    time_stamp = get_timestamp()
    user_ID = session["user_id"]
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



