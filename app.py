import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Integer, String
from typing import List

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create db object using SQLAlchemy constructor
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

# configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

# configure models for tables
class User(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)

    username:Mapped[str] = mapped_column(unique=True, nullable=False)
    hash:Mapped[str] = mapped_column(nullable=False)

    accounts:Mapped[List["Account"]] = relationship(back_populates="user")


class Account(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("user.id"),nullable=False)

    category:Mapped[str] = mapped_column(nullable=False)
    name:Mapped[str] = mapped_column(nullable=False)

    user:Mapped["User"] = relationship(back_populates="accounts")
    transactions:Mapped[List["Transaction"]] = relationship(back_populates="account")

class Transaction(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    account_id:Mapped[int] = mapped_column(ForeignKey("account.id"),nullable=False)

    date:Mapped[str] = mapped_column(nullable=False)
    name:Mapped[str] = mapped_column(nullable=False)
    category:Mapped[str] = mapped_column(nullable=False)
    account:Mapped[str] = mapped_column(nullable=False)
    amount:Mapped[int] = mapped_column(nullable=False)

    account:Mapped["Account"] = relationship(back_populates="transactions")

# create tables
with app.app_context():
    db.create_all()

# Keep's track if title animation has been loaded
animationLoaded = []

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Show homepage
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password")

        # Query database for username
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.session.execute(db.select(User).where(User.username == username)).scalar()
        if user == None:
            return apology("User does not exist")

        # Ensure username exists and password is correct
        if not check_password_hash(user.hash, password):
            return apology("Invalid password")

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", animationLoaded = animationLoaded)
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        usernameCheck = db.session.execute(db.select(User.username).where(User.username == username)).scalar()
        if usernameCheck != None:
            if username == usernameCheck:
                return apology("Username already exists")
        elif username == "":
            return apology("Username is blank")
        elif password == "":
            return apology("Password is blank")
        elif confirmation == "":
            return apology("Confirmation is blank")
        elif password != confirmation:
            return apology("Password does not equal confirmation")
        else:
            hashedPassword = generate_password_hash(password)
            user = User(
                username = username,
                hash = hashedPassword
            )
            db.session.add(user)
            db.session.commit()
            return redirect("/login")
    else:
        return render_template("register.html")