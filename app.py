from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    GUEST_ACCOUNT_ID,
    apology,
    loginRequired,
    usd,
    currentDate,
    checkGuest,
    getUserByID,
    getUserAccounts,
    getAccount,
    getUserAccountsID,
    getTransaction,
    getAccountTransactions,
    getAccountsTransactions,
    getMonthTotals,
    getTypeTotals,
    isBlank,
    getUser,
    isInt,
    isFloat,
)
from models import db, User, Account, Transaction

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

# create SQL tables
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
@loginRequired
def index():
    userID = session["user_id"]

    # Get account information
    accounts = getUserAccounts(userID)
    checkingTotal = getTypeTotals(accounts, "Checking")
    savingsTotal = getTypeTotals(accounts, "Savings")

    # Get transaction information
    userAccountsID = getUserAccountsID(userID)
    allTransactions = getAccountsTransactions(userAccountsID)

    monthTotals = getMonthTotals(userAccountsID)

    # Only show latest transactions
    transactions = []
    counter = 0
    for transaction in allTransactions:
        if counter < 5:
            transactions.append(transaction)
            counter += 1

    return render_template(
        "home.html",
        accounts=accounts,
        checkingTotal=checkingTotal,
        savingsTotal=savingsTotal,
        transactions=transactions,
        monthTotals=monthTotals,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        checkGuestLogin = request.form.get("guestForm")
        print(checkGuestLogin)
        if checkGuestLogin == "GUEST_LOGIN":
            user = getUserByID(GUEST_ACCOUNT_ID)
            session["user_id"] = user.id
            return redirect("/")

        # Query database for username
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure inputs are submitted
        if isBlank(username):
            return apology("Must provide username")
        if isBlank(password):
            return apology("Must provide password")

        user = getUser(username)
        if isBlank(user):
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
        return render_template("login.html", animationLoaded=animationLoaded)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        allUsernames = db.session.execute(db.select(User.username)).scalars().all()

        if username in allUsernames:
            return apology("User already exists")
        elif isBlank(username):
            return apology("Must provide username")
        elif isBlank(password):
            return apology("Must provide password")
        elif isBlank(confirmation):
            return apology("Must provide a confirmation password")
        elif password != confirmation:
            return apology("Password does not equal confirmation")
        else:
            hashedPassword = generate_password_hash(password)
            user = User(username=username, hash=hashedPassword)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/accounts")
@loginRequired
def accounts():
    userID = session["user_id"]
    accounts = getUserAccounts(userID)
    checkingTotal = getTypeTotals(accounts, "Checking")
    savingsTotal = getTypeTotals(accounts, "Savings")

    return render_template(
        "accounts.html",
        accounts=accounts,
        checkingTotal=checkingTotal,
        savingsTotal=savingsTotal,
    )


@app.route("/addAccount", methods=["GET", "POST"])
@loginRequired
def addAccount():
    userID = session["user_id"]
    # Add account for user
    if request.method == "POST":
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")

        name = request.form.get("name")

        if isBlank(name):
            return apology("Must provide a name")

        account = Account(user_id=userID, category=category, name=name, balance=0)
        db.session.add(account)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("add_accounts.html")


@app.route("/transactions")
@loginRequired
def transactions():
    userID = session["user_id"]
    userAccountsID = getUserAccountsID(userID)
    transactions = getAccountsTransactions(userAccountsID)
    return render_template("transactions.html", transactions=transactions)


@app.route("/addTransaction", methods=["GET", "POST"])
@loginRequired
def addTransaction():
    # Add transaction to account
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")

        dateTime = currentDate()
        transactionType = request.form.get("type")
        name = request.form.get("name")
        category = request.form.get("category")
        accountID = request.form.get("account")
        amount = request.form.get("amount")

        if isBlank(name):
            return apology("Must provide a name")
        if isBlank(category):
            return apology("Must provide a category")
        if isBlank(amount):
            return apology("Please input an amount")

        if not isFloat(amount):
            return apology("Please input a number for the transaction amount")

        accountID = int(accountID)
        amount = float(amount)
        account = getAccount(accountID)

        if amount <= 0:
            return apology("Please input a positive amount")

        transaction = Transaction(
            account_id=accountID,
            date=dateTime,
            transactionType=transactionType,
            name=name,
            category=category,
            accountName=account.name,
            amount=amount,
        )
        balance = account.balance
        if transactionType == "Expense":
            if balance < amount:
                return apology("You do not have enough balance for this transaction")
            balance -= amount
            account.balance = balance
        else:
            balance += amount
            account.balance = balance
        db.session.add(transaction)
        db.session.commit()
        return redirect("/")
    else:
        accounts = getUserAccounts(userID)
        return render_template("add_transaction.html", accounts=accounts)


@app.route("/transfer", methods=["GET", "POST"])
@loginRequired
def transfer():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")
        dateTime = currentDate()
        fromID = request.form.get("from")
        toID = request.form.get("to")
        amount = request.form.get("amount")

        if isBlank(amount):
            return apology("Please input an amount")
        if fromID == toID:
            return apology("Can't transfer to the same account")

        if not isFloat(amount):
            return apology("Please input a number for the transfer amount")

        fromID = int(fromID)
        toID = int(toID)

        fromAccount = getAccount(fromID)
        toAccount = getAccount(toID)

        if amount <= 0:
            return apology("Please input a positive amount")
        if fromAccount.balance < amount:
            return apology("You do not have enough balance for this transfer")

        fromAccount.balance -= amount
        toAccount.balance += amount
        transaction = Transaction(
            account_id=fromID,
            date=dateTime,
            transactionType="Transfer",
            name="Internal Transfer",
            category="Transfer",
            accountName=fromAccount.name,
            amount=amount,
        )
        db.session.add(transaction)
        db.session.commit()
        return redirect("/")
    else:
        accounts = getUserAccounts(userID)
        return render_template("transfer.html", accounts=accounts)


@app.route("/editAccount", methods=["GET", "POST"])
@loginRequired
def editAccount():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")
        accountID = request.form.get("accountID")
        name = request.form.get("name")
        category = request.form.get("category")
        account = getAccount(accountID)

        if isBlank(name):
            return apology("Please input a name")

        account.name = name
        account.category = category
        db.session.commit()
        return redirect("/")
    else:
        accountID = request.args.get("accountID")
        return render_template("edit_account.html", accountID=accountID)


@app.route("/deleteAccount", methods=["POST"])
@loginRequired
def deleteAccount():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")
        accountID = request.form.get("accountID")
        account = getAccount(accountID)
        # Delete transactions for account
        transactions = getAccountTransactions(accountID)
        for transaction in transactions:
            db.session.delete(transaction)
        db.session.delete(account)
        db.session.commit()
        return redirect("/")


@app.route("/editTransaction", methods=["GET", "POST"])
@loginRequired
def editTransaction():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")
        transaction = getTransaction(transactionID)
        transactionID = request.form.get("transactionID")
        name = request.form.get("name")
        category = request.form.get("category")
        if isBlank(name):
            return apology("Please input a name")
        if isBlank(category):
            return apology("Please input a category")
        transaction.name = name
        transaction.category = category
        db.session.commit()
        return redirect("/")
    else:
        transactionID = request.args.get("transactionID")
        accounts = getUserAccounts(userID)
        return render_template(
            "edit_transaction.html", transactionID=transactionID, accounts=accounts
        )


@app.route("/deleteTransaction", methods=["POST"])
@loginRequired
def deleteTransaction():
    if request.method == "POST":
        userID = session["user_id"]
        if checkGuest(userID):
            return apology("Guests can't modify transactions or accounts")
        transactionID = request.form.get("transactionID")
        transaction = getTransaction(transactionID)
        # Find account
        account = getAccount(transaction.account_id)
        if transaction.transactionType == "Expense":
            account.balance += transaction.amount
        else:
            if account.balance < transaction.amount:
                return apology(
                    "If you delete this transaction the account balance will be negative"
                )
            account.balance -= transaction.amount
        db.session.delete(transaction)
        db.session.commit()
        return redirect("/")
