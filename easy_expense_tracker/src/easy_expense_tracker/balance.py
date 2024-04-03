from typing import Optional, List
from sqlalchemy import ForeignKey, String, Double, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import os

BALANCE_ENTRIES_TABLE="balance_entries"
CATEGORIES_TABLE="categories"
BANK_ACCOUNTS_TABLE="bank_accounts"
AMOUNT_DETAIL_TABLE="amount_detail"

class Base(DeclarativeBase):
    pass

class BalanceEntry(Base):
    __tablename__ = BALANCE_ENTRIES_TABLE
    id : Mapped[int] = mapped_column(primary_key=True)
    bank_account_id : Mapped[int] = mapped_column(ForeignKey(f"{BANK_ACCOUNTS_TABLE}.id"))
    bank_account : Mapped["BankAccount"] = relationship()
    timestamp: Mapped[float] = mapped_column(Double(3))
    amount_detail : Mapped[List["AmountDetail"]] = relationship(back_populates="balance_entry")
    amount : Mapped[float] = mapped_column(Double(2))
    description: Mapped[str] = mapped_column(String(64))
    digest: Mapped[str] = mapped_column(String(64))
    cash_flow : Mapped[int] = mapped_column(String(1))
    due_date : Mapped[float] = mapped_column(Double(3))
    doc_id : Mapped[str] = mapped_column(String(64))


class AmountDetail(Base):
    __tablename__ = AMOUNT_DETAIL_TABLE
    id : Mapped[int] = mapped_column(primary_key=True)
    balance_entry_id : Mapped[int] = mapped_column(ForeignKey(f"{BALANCE_ENTRIES_TABLE}.id"))
    balance_entry : Mapped["BalanceEntry"] = relationship(back_populates="amount_detail")
    timestamp : Mapped[float] = mapped_column(Double(3))
    amount : Mapped[float] = mapped_column(Double(2))
    cash_flow : Mapped[int] = mapped_column(String(1))
    category_id : Mapped[int] = mapped_column(ForeignKey(f"{CATEGORIES_TABLE}.id"))
    category : Mapped["Category"] = relationship()
    annotation: Mapped[str] = mapped_column(String(128))


class Category(Base):
    __tablename__ = CATEGORIES_TABLE
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(30))
    expense : Mapped[bool] = mapped_column(default=True)


class BankAccount(Base):
    __tablename__ = BANK_ACCOUNTS_TABLE
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(30))
    credit : Mapped[bool] = mapped_column(default=False)


def connect_sqlite_db(file_path):
    if not os.path.exists(file_path):
        print(_("Database {db} not found").format(db=file_path))
        quit(2)
    engine = create_engine(f"sqlite:///{file_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine

