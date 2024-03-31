from .balance import Category, BankAccount, BalanceEntry, Base, AmountDetail
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, delete, or_
from datetime import datetime, timezone

import os
import locale

INSTRUCTIONS = {
    "UPDATED_RECORDS": "{count} records updated"
}

def category_prompt_help():
    print("q".rjust(6), ":", _("Abort current session without saving"))
    print(".".rjust(6), ":", _("Stop review"))
    print("*".rjust(6), ":", _("Show all category"))
    print(_("id").rjust(6), ":", _("Numeric identification of a previously created category"))
    print(_("name").rjust(6), ":", _("Name of a previously created category"))
    print(";".rjust(6), ":", _("Optionally use this separator as described bellow"))
    print("".rjust(6), " ", _("To annotate the amount with a personal description (ex. Meal;Happy hour)"))
    print("".rjust(6), " ", _("To split the amount in multiple categories enter an amount lesser then the total (ex. Meal;50.00)"))
    print("".rjust(6), " ", _("For both split and annotate enter the amount then the annotation (ex. Meal;50.00;Happy hour)"))
    print("".rjust(6), " ", _("When splitting the remaining amount will be prompted until the total amount is fullfiled"))

def show_categories(session : Session):
    for c in session.query(Category).filter().order_by(Category.name):
        print(str(c.id).rjust(2), c.name)


def get_no_category_id(session : Session):
    return 


def add_category(session: Session, category_name, is_expense):
    category = session.query(Category).filter(Category.name == category_name).first()
    if not category:
        new_category = Category(name = category_name, expense = is_expense)
        session.add(new_category)
        session.commit()
        return new_category.id
    return category.id

def parse_user_input(user_input):
    params = {}
    tokens = user_input.split(';')
    if len(tokens) > 0:
        params.update({'category': tokens[0]})
        if len(tokens) > 1:
            try:
                params.update({'amount': locale.atof(tokens[1])})
            except ValueError:
                params.update({'annotation': tokens[1]})
            if len(tokens) > 2:
                params.update({'annotation': tokens[2]})
    return params

def intValue(string, default):
    try:
        return int(string)
    except ValueError:
        return default

def prompt_category(session : Session):
    while True:
        user_input = input(_('Category ID, name to add or ?: '))
        try:
            if not user_input:
                continue
            if user_input == '*':
                show_categories(session)
                continue
            elif user_input == '.':
                break
            elif user_input == 'q':
                quit()
            elif user_input == '?':
                category_prompt_help()
            else:
                params = parse_user_input(user_input)
                if 'category' in params:
                    result = session.query(Category).filter(or_(Category.id == intValue(params.get('category'), -1), Category.name == params.get('category')))
                    if result.count() > 0:
                        params.update({'category': result.first().name})
                        params.update({'category_id': result.first().id})
                    else:
                        is_expense = input(_('Is it an expense? '))
                        if not is_expense.lower().startswith(_('y')) and not is_expense.lower().startswith(_('n')):
                            print(_('Answer yes or no. Category was not created, try again.'))
                            continue
                        params.update({'category_id': add_category(session, params.get('category'), True if is_expense.startswith(_('y')) else False)})
                else:
                    params = None
                return params
        except IOError:
            pass
    return None


def connect_db(args):
    if not os.path.exists(args.database):
        print(_("Database {db} not found").format(db=args.database))
        quit(2)
    engine = create_engine(f"sqlite:///{args.database}", echo=False)
    Base.metadata.create_all(engine)
    return engine

    
def format_balance_entry(entry):
    return {
        'timestamp': datetime.fromtimestamp(entry.timestamp, timezone.utc).strftime("%Y-%m-%d"),
        'description': entry.description,
        'amount': str(entry.amount)
    }

def int_val(value):
    return int(value * 100)


def do_review(args):
    engine = connect_db(args)
    did_update = 0
    with Session(engine) as session:
        no_category = session.query(Category).filter(Category.name == 'No Category').first()
        if not no_category:
            print(_("Nothing to review"))
            quit(0)
        for entry in session.query(BalanceEntry).where(BalanceEntry.amount_detail.any(AmountDetail.category == no_category)):
            print('-' * 15)
            print("{timestamp} {description} {amount}".format(**format_balance_entry(entry)))
            print('-' * 15)
            amount_details = []
            current_amount = 0
            while int_val(current_amount) < int_val(entry.amount):
                category_details = prompt_category(session)
                if not category_details:
                    break
                amount_detail = {
                    'category_id': category_details.get('category_id'),
                    'amount': category_details.get('amount', entry.amount - current_amount),
                    'annotation': category_details.get('annotation', ''),
                    'timestamp': entry.timestamp,
                    'balance_entry_id': entry.id
                }
                if int_val(amount_detail.get('amount') + current_amount) > int_val(entry.amount):
                    print(_('Balance entry amount exceeded'))
                    continue
                current_amount += amount_detail.get('amount')
                diff = entry.amount - current_amount
                if int_val(diff) != 0:
                    print(f"{diff:.2f} remaining, please add a category to it.")
                amount_details.append(amount_detail)
            if len(amount_details) > 0:
                session.execute(delete(AmountDetail).where(AmountDetail.balance_entry_id == entry.id))
                for ad in amount_details:
                    session.add(AmountDetail(**ad))
                    did_update += 1
            else:
                break
        if did_update:
            session.commit()
            print(_("{count} records updated").format(count=did_update))
    if did_update == 0:
        print(_("Nothing changed"))

