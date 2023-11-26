import datetime, calendar
from models import db, User, Account, Transaction
from flask import redirect, render_template, session
from functools import wraps

GUEST_ACCOUNT_ID = 1


def loginRequired(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decoratedFunction


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def currentDate():
    dateTime = datetime.datetime.now()
    dateTime = dateTime.strftime("%x")
    dateTime = dateTime[:-3]
    return dateTime


def checkGuest(userID):
    if userID == GUEST_ACCOUNT_ID:
        return True
    return False


def isBlank(data):
    if data is None or data == "":
        return True
    return False


def isFloat(data):
    try:
        data = float(data)
    except (ValueError, TypeError):
        return False
    else:
        return True


# Get user
def getUser(username):
    user = db.session.execute(db.select(User).where(User.username == username)).scalar()
    return user


def getUserByID(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    return user


# Get a single account
def getAccount(accountID):
    account = db.session.execute(
        db.select(Account).where(Account.id == accountID)
    ).scalar()
    return account


# Get all the user's accounts
def getUserAccounts(userID):
    accounts = (
        db.session.execute(db.select(Account).where(Account.user_id == userID))
        .scalars()
        .all()
    )
    return accounts


# Get all the user's accounts ID's
def getUserAccountsID(userID):
    accounts = (
        db.session.execute(db.select(Account.id).where(Account.user_id == userID))
        .scalars()
        .all()
    )
    return accounts


# Get a single transaction
def getTransaction(transactionID):
    transaction = db.session.execute(
        db.select(Transaction).where(Transaction.id == transactionID)
    ).scalar()
    return transaction


# Get transactions for a single account
def getAccountTransactions(accountID):
    transactions = (
        db.session.execute(
            db.select(Transaction).where(Transaction.account_id == accountID)
        )
        .scalars()
        .all()
    )
    return transactions


# Get transactions for multiple accounts
def getAccountsTransactions(userAccountsID):
    transactions = (
        db.session.execute(
            db.select(Transaction)
            .where(Transaction.account_id.in_(userAccountsID))
            .order_by(Transaction.id.desc())
        )
        .scalars()
        .all()
    )
    return transactions


def getTypeTotals(accounts, type):
    typeTotal = 0
    if type == "Checking":
        for account in accounts:
            if account.category == "Checking":
                typeTotal += account.balance
    elif type == "Savings":
        for account in accounts:
            if account.category == "Savings":
                typeTotal += account.balance
    return typeTotal


# Get month to month data to build the charts
def getMonthTotals(userAccountsID):
    monthTotals = []
    # Get all the user's transactions
    transactions = (
        db.session.execute(
            db.select(Transaction)
            .where(Transaction.account_id.in_(userAccountsID))
            .order_by(Transaction.id.asc())
        )
        .scalars()
        .all()
    )
    balance = 0
    for transaction in transactions:
        monthExists = False
        # Conver the transaction date in the database to only the month date
        monthNumber = int(transaction.date[:-3])
        # Get the month number
        monthName = calendar.month_name[monthNumber]
        for month in monthTotals:
            # Check if month exists in list already
            if month["Month"] == monthName:
                monthExists = True
        # If it exists then update values
        if monthExists == True:
            if transaction.transactionType == "Expense":
                expenses = month["Expenses"] + int(transaction.amount)
                balance -= int(transaction.amount)
                month["Expenses"] = expenses
                month["Balance"] = balance
            elif transaction.transactionType == "Income":
                income = month["Income"] + int(transaction.amount)
                balance += int(transaction.amount)
                month["Income"] = income
                month["Balance"] = balance
        # If it doesn't exist, then append the first transaction with that month
        else:
            if transaction.transactionType == "Expense":
                balance -= int(transaction.amount)
                transactionDict = {
                    "monthNumber": monthNumber,
                    "Month": monthName,
                    "Expenses": int(transaction.amount),
                    "Income": 0,
                    "Balance": balance,
                }
                monthTotals.append(transactionDict)
            elif transaction.transactionType == "Income":
                balance += int(transaction.amount)
                transactionDict = {
                    "monthNumber": monthNumber,
                    "Month": monthName,
                    "Expenses": 0,
                    "Income": int(transaction.amount),
                    "Balance": balance,
                }
                monthTotals.append(transactionDict)

    return monthTotals
