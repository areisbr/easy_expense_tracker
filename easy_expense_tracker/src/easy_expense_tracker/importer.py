from .balance import Category, BankAccount, BalanceEntry, AmountDetail, Base
from sqlalchemy.orm import Session
from hashlib import sha256
from datetime import datetime, timezone

from sqlalchemy import create_engine

DUPLICATE_DATA_CSV_FILE_CODE = 100


def get_category(name, session):
    if not name:
        name = 'No Category'
    result = session.query(Category).filter_by(name=name).first()
    return Category(name=name) if not result else result


def get_bank_account(name, credit, session):
    result = session.query(BankAccount).filter_by(name=name).first()
    return BankAccount(name=name, credit=credit) if not result else result


def get_due_date(args) -> int:
    due_date = 0
    if args.due_date:
        due_date = datetime.strptime(args.due_date, '%Y-%m-%d').timestamp()
    return due_date


def get_digest(entry : dict) -> str:
    encoded = ''.join((
        entry.get("bank_account").name,
        entry.get("description"),
        entry.get("doc_id"),
        str(entry.get("timestamp")),
        str(entry.get("amount"))
    )).encode('utf-8')
    return sha256(encoded).hexdigest()
    

def is_duplicate(session : Session, entry : dict) -> bool:
    digest = entry.get("digest")
    balance_entry = session.query(BalanceEntry).filter_by(digest=digest).first()
    return True if balance_entry and balance_entry.digest == digest else False


def is_duplicate_digest_list(digest_list : list, entry : dict) -> bool:
    digest = entry.get("digest")
    return True if digest in digest_list else False


def do_import(extract_fun, args, success_fun, error_fun):
    engine = create_engine(f"sqlite:///{args.database}", echo=False)
    Base.metadata.create_all(engine)
    import_count = 0
    digest_list = []
    with Session(engine) as session:
        for result in extract_fun(args):
            entry = {
                "bank_account": get_bank_account(result.template, args.due_date != None, session),
                "timestamp": result.timestamp,
                "amount": result.amount,
                "amount_detail": [AmountDetail(
                    timestamp=result.timestamp,
                    amount=result.amount,
                    category=get_category(result.category, session),
                    annotation=result.annotation)],
                "doc_id": result.doc_id if result.doc_id else '',
                "description": result.description,
                "cash_flow": result.cash_flow.upper(),
                "due_date": get_due_date(args)
            }
            entry.update({"digest": get_digest(entry)})

            if is_duplicate_digest_list(digest_list, entry):
                error_fun({
                    "status": DUPLICATE_DATA_CSV_FILE_CODE,
                    "message": str(result)
                })
                continue
            else:
                digest_list.append(entry.get("digest"))

            if is_duplicate(session, entry):
                continue

            entry = BalanceEntry(**entry)
            session.add(entry)
            session.commit()
            import_count += 1
        success_fun({
            "status": 0,
            "imported_records": import_count
        })
