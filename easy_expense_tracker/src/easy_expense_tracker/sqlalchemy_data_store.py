from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .data_store import DataStore
from .balance import Category, BankAccount, BalanceEntry, AmountDetail, Base

class SQLAlchemyDataStore(DataStore):

    def __init__(self, session):
        self.session = session


    def create_balance_entry(self, entry):
        bank_account = self._get_bank_account_by_name(entry.get('bank_account').get('name'))
        with self.session as s:
            for amount_detail in entry.get('amount_detail'):
                category = self._get_category_by_name(amount_detail.get('category'))
                amount_detail.update({'category': category if category else Category(name=amount_detail.get('category'))})
            entry.update({'amount_detail': [AmountDetail(**x) for x in entry.get('amount_detail')]})
            entry.update({'bank_account': bank_account if bank_account else BankAccount(**entry.get('bank_account'))})
            tmp = BalanceEntry(**entry)
            s.add(tmp)
            s.commit()


    def get_balance_entry_by_digest(self, digest):
        with self.session as s:
            result = s.query(BalanceEntry).filter_by(digest=digest)
            if result.count() > 0:
                entry = result.first()
                return {
                    "id": entry.id,
                    "bank_account_id": entry.bank_account_id,
                    "timestamp": entry.timestamp,
                    "amount": entry.amount,
                    "description": entry.description,
                    "digest": entry.digest,
                    "cash_flow": entry.cash_flow,
                    "due_date": entry.due_date,
                    "doc_id": entry.doc_id
                }


    def create_sqlite_session(location, echo=False):
        engine = create_engine(f"sqlite:///{location}", echo=echo)
        Base.metadata.create_all(engine)
        return Session(engine)


    def _get_category_by_name(self, name):
        with self.session as s:
            result = s.query(Category).filter_by(name=name)
            if result.count() > 0:
                return result.first()


    def _get_bank_account_by_name(self, name):
        with self.session as s:
            result = s.query(BankAccount).filter_by(name=name)
            if result.count() > 0:
                return result.first()


