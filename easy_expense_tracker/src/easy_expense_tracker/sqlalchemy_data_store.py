from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from .data_store import DataStore
from .balance import Category, BankAccount, BalanceEntry, AmountDetail, Base

class SQLAlchemyDataStore(DataStore):

    def __init__(self, session):
        self.session = session


    def create_sqlite_session(location, echo=False):
        engine = create_engine(f"sqlite:///{location}", echo=echo)
        Base.metadata.create_all(engine)
        return Session(engine)


    def create_balance_entry(self, entry):
        bank_account = self._get_bank_account_by_name(entry.get('bank_account').get('name'))
        with self.session as s:
            for amount_detail in entry.get('amount_detail'):
                category = self._get_category_by_name(s, amount_detail.get('category'))
                amount_detail.update({'category': category if category else Category(name=amount_detail.get('category'))})
            entry.update({'amount_detail': [AmountDetail(**x) for x in entry.get('amount_detail')]})
            entry.update({'bank_account': bank_account if bank_account else BankAccount(**entry.get('bank_account'))})
            tmp = BalanceEntry(**entry)
            s.add(tmp)
            s.commit()

    def create_category(self, category):
        with self.session as s:
            new_category = Category(**category)
            s.add(new_category)
            s.commit()
            return self._category_as_dictionary(new_category)


    def create_amount_detail_items(self, amount_detail_list):
        with self.session as s:
            for amount_detail in amount_detail_list:
                s.add(AmountDetail(**amount_detail))
            s.commit()


    def get_categories(self, order_by='name'):
        with self.session as s:
            result = s.query(Category).filter().order_by(order_by)
            return [ self._category_as_dictionary(x) for x in result ]


    def get_balance_entry_by_digest(self, digest):
        with self.session as s:
            result = s.query(BalanceEntry).filter_by(digest=digest)
            if result.count() > 0:
                return _balance_entry_as_dictionary(result.first())


    def get_category_by_name(self, name):
        with self.session as s:
            category = self._get_category_by_name(s, name)
            if category:
                return self._category_as_dictionary(category)


    def get_category_by_id(self, cid):
        with self.session as s:
            if cid >= 0:
                result = s.query(Category).filter(Category.id == cid)
                if result.count() > 0:
                    return self._category_as_dictionary(result.first())


    def get_balance_entries_by_amount_detail_category_name(self, category_name):
        with self.session as s:
            category = self._get_category_by_name(s, category_name)
            if category:
                result = s.query(BalanceEntry).where(BalanceEntry.amount_detail.any(AmountDetail.category == category))
                if result.count() > 0:
                    return [ self._balance_entry_as_dictionary(x) for x in result ]


    def delete_all_amount_detail_by_balance_entry_id(self, bid):
        with self.session as s:
            result = s.execute(delete(AmountDetail).where(AmountDetail.balance_entry_id == bid))


    def _get_category_by_name(self, session, name):
            result = session.query(Category).filter_by(name=name)
            if result.count() > 0:
                return result.first()


    def _get_bank_account_by_name(self, name):
        with self.session as s:
            result = s.query(BankAccount).filter_by(name=name)
            if result.count() > 0:
                return result.first()


    def _category_as_dictionary(self, category):
        return {
            'name': category.name,
            'id': category.id,
            'expense': category.expense
        }

    def _balance_entry_as_dictionary(self, balance_entry):
        return {
            'id': balance_entry.id,
            'bank_account_id': balance_entry.bank_account_id,
            'timestamp': balance_entry.timestamp,
            'amount': balance_entry.amount,
            'description': balance_entry.description,
            'digest': balance_entry.digest,
            'cash_flow': balance_entry.cash_flow,
            'due_date': balance_entry.due_date,
            'doc_id': balance_entry.doc_id
        }
