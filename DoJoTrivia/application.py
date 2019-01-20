from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

app = Flask(__name__)

def apology(message):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", bottom=escape(message))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation") or not request.form.get("emailaddress"):
            return apology("Make sure to fill out all fields!")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match!")
    else:
        return render_template("register.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")

@app.route("/about-us")
def aboutus():
    return render_template("about-us.html")

@app.route("/personal")
def personal():
    return render_template("personal-page.html")

@app.route("/createquiz")
def createquiz():
    return render_template("createquiz.html")

@app.route("/creategame")
def creategame():
    return render_template("creategame.html")

@app.route("/joingame")
def joingame():
    return render_template("joining.html")

@app.route("/makeq")
def makeq():
    return render_template("makeq.html")