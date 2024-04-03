class DataStore:
    def create_balance_entry(self, entry):
        pass

    def create_amount_detail_items(self, amount_detail_list):
        pass

    def create_category(self, category):
        pass

    def get_categories(order_by='name'):
        pass

    def get_balance_entry_by_digest(self, digest):
        pass

    def get_category_by_id(self, category_id):
        pass

    def get_category_by_name(self, name):
        pass

    def get_bank_account_by_name(self, name):
        pass

    def get_balance_entries_by_amount_detail_category(self, name):
        pass

    def delete_all_amount_detail_by_balance_entry_id(self, bid):
        pass
