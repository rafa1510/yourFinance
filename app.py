from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    get_flashed_messages,
)
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    GUEST_ACCOUNT_ID,
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
    # Clear user ID if user is logged in
    try:
        if session["user_id"]:
            session.clear()
    except:
        pass

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
            flash("Must provide username", "error")
            return redirect("/login")
        if isBlank(password):
            flash("Must provide password", "error")
            return redirect("/login")

        user = getUser(username)
        if isBlank(user):
            flash("User does not exist", "error")
            return redirect("/login")

        # Ensure username exists and password is correct
        if not check_password_hash(user.hash, password):
            flash("Invalid password", "error")
            return redirect("/login")

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
            flash("User already exists", "error")
            return redirect("/register")
        elif isBlank(username):
            flash("Must provide username", "error")
            return redirect("/register")
        elif isBlank(password):
            flash("Must provide password", "error")
            return redirect("/register")
        elif isBlank(confirmation):
            flash("Must provide a confirmation password", "error")
            return redirect("/register")
        elif password != confirmation:
            flash("Password does not equal confirmation", "error")
            return redirect("/register")
        else:
            hashedPassword = generate_password_hash(password)
            user = User(username=username, hash=hashedPassword)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created", "success")
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


@app.route("/transactions")
@loginRequired
def transactions():
    userID = session["user_id"]
    userAccountsID = getUserAccountsID(userID)
    transactions = getAccountsTransactions(userAccountsID)
    return render_template("transactions.html", transactions=transactions)


@app.route("/transfer", methods=["GET", "POST"])
@loginRequired
def transfer():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            flash("Guests can't input transfers", "error")
            return redirect("/transfer")
        dateTime = currentDate()
        fromID = request.form.get("from")
        toID = request.form.get("to")
        amount = request.form.get("amount")

        if isBlank(amount):
            flash("Please input an amount", "error")
            return redirect("/transfer")
        if fromID == toID:
            flash("Can't transfer to the same account", "error")
            return redirect("/transfer")

        if not isFloat(amount):
            flash("Please input a number for the transfer amount", "error")
            return redirect("/transfer")

        fromID = int(fromID)
        toID = int(toID)
        amount = float(amount)

        fromAccount = getAccount(fromID)
        toAccount = getAccount(toID)

        if amount <= 0:
            flash("Please input a positive amount", "error")
            return redirect("/transfer")
        if fromAccount.balance < amount:
            flash("Account does not have enough balance for this transfer", "error")
            return redirect("/transfer")

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
        flash("Transfer successful", "success")
        return redirect("/")
    else:
        accounts = getUserAccounts(userID)
        return render_template("transfer.html", accounts=accounts)


@app.route("/addAccount", methods=["GET", "POST"])
@loginRequired
def addAccount():
    userID = session["user_id"]
    # Add account for user
    if request.method == "POST":
        if checkGuest(userID):
            flash("Guests can't add accounts", "error")
            return redirect("/addAccount")

        name = request.form.get("name")
        category = request.form.get("category")

        if isBlank(name):
            flash("Must provide a name", "error")
            return redirect("/addAccount")

        account = Account(user_id=userID, category=category, name=name, balance=0)
        db.session.add(account)
        db.session.commit()
        flash("Account has been added", "success")
        return redirect("/")
    else:
        return render_template("add_accounts.html")


@app.route("/addTransaction", methods=["GET", "POST"])
@loginRequired
def addTransaction():
    # Add transaction to account
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            flash("Guests can't add transactions", "error")
            return redirect("/addTransaction")

        dateTime = currentDate()
        transactionType = request.form.get("type")
        name = request.form.get("name")
        category = request.form.get("category")
        accountID = request.form.get("account")
        amount = request.form.get("amount")

        if isBlank(name):
            flash("Must provide a name", "error")
            return redirect("/addTransaction")
        if isBlank(category):
            flash("Must provide a category", "error")
            return redirect("/addTransaction")
        if isBlank(amount):
            flash("Please input an amount", "error")
            return redirect("/addTransaction")

        if not isFloat(amount):
            flash("Please input a number for the transaction amount", "error")
            return redirect("/addTransaction")

        accountID = int(accountID)
        amount = float(amount)
        account = getAccount(accountID)

        if amount <= 0:
            flash("Please input a positive amount", "error")
            return redirect("/addTransaction")

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
                flash(
                    "Account does not have enough balance for this transaction", "error"
                )
                return redirect("/addTransaction")
            balance -= amount
            account.balance = balance
        else:
            balance += amount
            account.balance = balance
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction has been added", "success")
        return redirect("/")
    else:
        accounts = getUserAccounts(userID)
        return render_template("add_transaction.html", accounts=accounts)


@app.route("/editAccount", methods=["GET", "POST"])
@loginRequired
def editAccount():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            flash("Guests can't modify accounts", "error")
            return redirect("/editAccount")
        accountID = request.form.get("accountID")
        name = request.form.get("name")
        category = request.form.get("category")
        account = getAccount(accountID)

        if isBlank(name):
            flash("Please input a name", "error")
            return redirect("/editAccount")

        account.name = name
        account.category = category
        db.session.commit()
        flash("Account has been modified", "success")
        return redirect("/")
    else:
        accountID = request.args.get("accountID")
        return render_template("edit_account.html", accountID=accountID)


@app.route("/editTransaction", methods=["GET", "POST"])
@loginRequired
def editTransaction():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            flash("Guests can't modify transactions", "error")
            return redirect("/editTransaction")
        transactionID = request.form.get("transactionID")
        transaction = getTransaction(transactionID)
        name = request.form.get("name")
        category = request.form.get("category")
        if isBlank(name):
            flash("Please input a name", "error")
            return redirect("/editTransaction")
        if isBlank(category):
            flash("Please input a category", "error")
            return redirect("/editTransaction")
        transaction.name = name
        transaction.category = category
        db.session.commit()
        flash("Transaction has been modified", "success")
        return redirect("/")
    else:
        transactionID = request.args.get("transactionID")
        accounts = getUserAccounts(userID)
        return render_template(
            "edit_transaction.html", transactionID=transactionID, accounts=accounts
        )


@app.route("/deleteAccount", methods=["POST"])
@loginRequired
def deleteAccount():
    userID = session["user_id"]
    if request.method == "POST":
        if checkGuest(userID):
            flash("Guests can't delete accounts", "error")
            return redirect("/editAccount")
        accountID = request.form.get("accountID")
        account = getAccount(accountID)
        # Delete transactions for account
        transactions = getAccountTransactions(accountID)
        for transaction in transactions:
            db.session.delete(transaction)
        db.session.delete(account)
        db.session.commit()
        flash("Account has been deleted", "success")
        return redirect("/")


@app.route("/deleteTransaction", methods=["POST"])
@loginRequired
def deleteTransaction():
    if request.method == "POST":
        userID = session["user_id"]
        if checkGuest(userID):
            flash("Guests can't delete transactions", "error")
            return redirect("/editTransaction")
        transactionID = request.form.get("transactionID")
        transaction = getTransaction(transactionID)
        # Find account
        account = getAccount(transaction.account_id)
        if transaction.transactionType == "Expense":
            account.balance += transaction.amount
        else:
            if account.balance < transaction.amount:
                flash(
                    "Deleting this transaction will make the account balance negative",
                    "error",
                )
                return redirect("/editTransaction")
            account.balance -= transaction.amount
        db.session.delete(transaction)
        db.session.commit()
        flash("Transaction has been deleted", "success")
        return redirect("/")
