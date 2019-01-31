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

        send_register_mail(request.form.get("emailaddress"))

        return redirect(url_for("personal"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
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
    session.clear()
    return render_template("logout.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")

    send_contact_mail(request.form.get("emailaddress"))

    return render_template("contacted.html")


@app.route("/about-us")
def aboutus():
    return render_template("about-us.html")

@app.route("/personal")
@login_required
def personal():
    # create match history
    match_history = get_match_history(session['user_id'])

    # get wins, losses and ratio
    wlr = get_wlr(session['user_id'], session['username'])

    return render_template("personal-page.html", username = session['username'], match_history = match_history, wlr = wlr)


@app.route("/customquiz", methods = ['GET', 'POST'])
@login_required
def customquiz():
    if request.method == 'GET':
        return render_template("customquiz_title.html")

    # validate given quiztitle
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

    insert_quiz(quiz_title, question, cor_answer, w_answer1, w_answer2, w_answer3)

    return render_template("custom_question.html", test = [question, cor_answer, w_answer1, w_answer2, w_answer3], test2 = session['quiz'])


@app.route("/creategame", methods=["GET", "POST"])
@login_required
def creategame():
    if request.method == "GET":
        options = get_quizzes()
        return render_template("creategame.html", options = options, test3 = json.dumps(options), variable = 3)

    # initialize variables
    option = request.form.get("option")[1:-1]
    room_ID = generate()
    session['room_ID'] = room_ID
    session['question_number'] = 0

    # insert quiz into database
    quizzes = []
    if option == 'Random':
        random_quiz(session['room_ID'])
    else:
        selected_quiz(option, session['room_ID'])

    answers, cor_answer, question = quiz_values(room_ID, session['question_number'])
    return render_template("answer.html", room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question,  option = option)



@app.route("/joingame",  methods=["GET", "POST"])
@login_required
def joingame():
    if request.method == "GET":
        return render_template("joining.html")

    # check if room number exits and assign to session
    if not empty_room(int(request.form.get("room_num"))):
        return apology("This room number is invalid!")

    session['room_ID'] = int(request.form.get("room_num"))
    session['question_number'] = 0

    # join game
    if not insert_p2(session['user_id'], session['room_ID']):
        return apology('This room is full')

    answers, cor_answer, question = quiz_values(session['room_ID'], session['question_number'])
    return render_template('answer.html', room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question)

@app.route("/results")
@login_required
def ending_game():

    wait()
    game_info = db.execute("SELECT time, score_P1, score_P2 FROM game WHERE game_room == :room", room = session['room_ID'])
    time_stamp = game_info[0]['time']
    score_P1 = game_info[0]['score_P1']
    score_P2 = game_info[0]['score_P2']
    score_P1 = int(score_P1)
    score_P2 = int(score_P2)

    results = game_end(session['room_ID'])
    if results == 'Draw':
        return render_template("results.html", room = session['room_ID'], time = time_stamp, score_P1 = score_P1, score_P2 = score_P2, winner = "Draw")
    return render_template("results.html", room = session['room_ID'], time = time_stamp, score_P1 = score_P1, score_P2 = score_P2, winner = results[1], username1 = results[2] , username2 = results[3])

@app.route('/quizC', methods=['GET', 'POST'])
def correct_answer():
    wait_for_player(session['room_ID'])
    update_score(session['user_id'], session['room_ID'])

    # check if questions are left
    session['question_number'] += 1
    room_ID = session['room_ID']
    if session['question_number'] < quiz_length(session['room_ID']):
        answers, cor_answer, question = quiz_values(session['room_ID'], session['question_number'])
        return render_template('answer.html', room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question)

    insert_time(session['room_ID'])
    return redirect(url_for("ending_game"))

@app.route('/quizW', methods=['GET', 'POST'])
def wrong_answer():
    wait_for_player(session['room_ID'])

    # check if questions are left
    session['question_number'] += 1
    room_ID = session['room_ID']
    if session['question_number'] < quiz_length(session['room_ID']):
        answers, cor_answer, question = quiz_values(session['room_ID'], session['question_number'])
        return render_template('answer.html', room = session['room_ID'], answer0 = answers[0], answer1 = answers[1], answer2 = answers[2], answer3 = answers[3], coranswer = cor_answer, question = question)

    insert_time(session['room_ID'])
    return redirect(url_for("ending_game"))