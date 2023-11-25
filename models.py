from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Integer, String
from typing import List
from flask_sqlalchemy import SQLAlchemy

# Create db object using SQLAlchemy constructor
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

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
    balance:Mapped[int] = mapped_column(nullable=False)

    user:Mapped["User"] = relationship(back_populates="accounts")
    transactions:Mapped[List["Transaction"]] = relationship(back_populates="account")

class Transaction(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    account_id:Mapped[int] = mapped_column(ForeignKey("account.id"),nullable=False)

    date:Mapped[str] = mapped_column(nullable=False)
    transactionType:Mapped[str] = mapped_column(nullable=False)
    name:Mapped[str] = mapped_column(nullable=False)
    category:Mapped[str] = mapped_column(nullable=False)
    accountName:Mapped[str] = mapped_column(nullable=False)
    amount:Mapped[int] = mapped_column(nullable=False)

    account:Mapped["Account"] = relationship(back_populates="transactions")