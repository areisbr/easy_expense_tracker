from .balance import Category, BankAccount, BalanceEntry, AmountDetail, Base, connect_sqlite_db
from sqlalchemy.orm import Session
from sqlalchemy import Double, text, select, or_, and_
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from time import time

import unicodedata

MONTHLY_EXPENSES_BY_CATEGORY_TABLE = 'monthly_expenses_by_category'

def format_column_name(string):
    normalized = unicodedata.normalize('NFKD', string)
    return ''.join([char for char in normalized if not unicodedata.combining(char)]).replace(' ', '_').lower()


def monthly_expenses_by_category_table(session, contents):
    session.execute(text(f"DROP TABLE IF EXISTS {MONTHLY_EXPENSES_BY_CATEGORY_TABLE}"))
    table_columns = []
    for year_month, categories in dict(sorted(contents.items(), reverse=True)).items():
        for name, amount in dict(sorted(categories.items(), key=lambda i: i[1], reverse=True)).items():
            normalized = format_column_name(name)
            if not normalized in table_columns:
                table_columns.append(normalized)
    columns = ','.join(['year_month STRING NOT NULL'] + [f"{x} DOUBLE DEFAULT 0 NOT NULL" for x in table_columns])
    session.execute(text(f"CREATE TABLE {MONTHLY_EXPENSES_BY_CATEGORY_TABLE} ({columns})"))
    columns = ','.join(['year_month'] + table_columns)
    columns_ref = ','.join([':year_month'] + [f":{x}" for x in table_columns])
    for year_month, categories in contents.items():
        row = {format_column_name(k):v for k,v in categories.items()}
        row.update({'year_month': year_month})
        for c in table_columns:
            if not c in row.keys():
                row.update({c: 0})
        session.execute(text(f"INSERT INTO {MONTHLY_EXPENSES_BY_CATEGORY_TABLE} ({columns}) VALUES ({columns_ref})"), row)
    session.commit()

def monthly_expenses_by_category(args):
    engine = connect_sqlite_db(args.database)
    today = datetime.fromtimestamp(time(), tz=timezone.utc)
    categories = {}
    with Session(engine) as session:
        from_date = datetime.strptime(datetime.today().strftime('%Y-%m'), '%Y-%m')
        if args.from_date:
            from_date = datetime.strptime(args.from_date, '%Y-%m')
        to_date = (from_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        if args.to_date:
            to_date = datetime.strptime(args.to_date, '%Y-%m')
            to_date = (to_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        from_timestamp = from_date.timestamp()
        to_timestamp = to_date.timestamp()
        stmt = select(BalanceEntry.timestamp, BalanceEntry.due_date, AmountDetail.amount, Category.name)\
            .join(AmountDetail.balance_entry)\
            .join(AmountDetail.category)\
            .join(BalanceEntry.bank_account)\
            .where(and_(Category.expense == True,
                    or_(and_(BalanceEntry.timestamp >= from_timestamp, BalanceEntry.timestamp < to_timestamp, BankAccount.credit == False),
                        and_(BalanceEntry.due_date >= from_timestamp, BalanceEntry.due_date < to_timestamp, BankAccount.credit == True))))
        for row in session.execute(stmt):
            timestamp = row[0]
            due_date = row[1]
            amount = row[2]
            category = row[3]

            date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            if due_date != 0:
                date = datetime.fromtimestamp(due_date, tz=timezone.utc)
            date_key = f"{date.year}-{date.month:02d}"
            if not date_key in categories:
                categories.update({date_key: {}})
            if not category in categories.get(date_key):
                categories.get(date_key).update({category: 0})
            categories[date_key][category] += amount
        monthly_expenses_by_category_table(session, categories)


def do_aggregate(args):
    monthly_expenses_by_category(args)
