from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about-us")
def aboutus():
    return render_template("about-us.html")

@app.route("/createquiz")
def creategame():
    return render_template("createquiz.html")

@app.route("/joingame")
def joingame():
    return render_template("joining.html")

@app.route("/personal")
def personal():
    return render_template("personal-page.html")