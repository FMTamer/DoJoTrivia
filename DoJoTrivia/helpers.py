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
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", bottom=escape(message))



