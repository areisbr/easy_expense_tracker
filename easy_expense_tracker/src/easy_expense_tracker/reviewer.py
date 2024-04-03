from datetime import datetime, timezone

import os
import locale


def category_prompt_help():
    print("q".rjust(6), ":", _("Abort current session without saving"))
    print(".".rjust(6), ":", _("Stop review"))
    print("*".rjust(6), ":", _("Show all categories"))
    print(_("id").rjust(6), ":", _("Numeric identification of a previously created category"))
    print(_("name").rjust(6), ":", _("Name of a previously created category"))
    print(";".rjust(6), ":", _("Optionally use this separator as described bellow"))
    print("".rjust(6), " ", _("To annotate the amount with a personal description (ex. Meal;Happy hour)"))
    print("".rjust(6), " ", _("To split the amount in multiple categories enter an amount lesser then the total (ex. Meal;50.00)"))
    print("".rjust(6), " ", _("For both split and annotate enter the amount then the annotation (ex. Meal;50.00;Happy hour)"))
    print("".rjust(6), " ", _("When splitting the remaining amount will be prompted until the total amount is fullfiled"))


def show_categories(data_store):
    for c in data_store.get_categories():
        print(str(c.get('id')).rjust(2), c.get('name'))


def add_category(data_store, name, expense):
    category = data_store.get_category_by_name(name)
    if not category:
        category = {
            "name": name,
            "expense": expense
        }
        category = data_store.create_category(category)
    return category.get('id')


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


def prompt_category(data_store):
    while True:
        user_input = input(_('Category ID, name to add or ?: '))
        try:
            if not user_input:
                continue
            if user_input == '*':
                show_categories(data_store)
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
                    if params.get('category').isnumeric():
                        category = data_store.get_category_by_id(int(params.get('category')))
                    else:
                        category = data_store.get_category_by_name(params.get('category'))

                    if category:
                        params.update({'category': category.get('name')})
                        params.update({'category_id': category.get('id')})
                    else:
                        is_expense = input(_('Is it an expense [yes|no]? ')).lower()
                        if not is_expense.startswith(_('y')) and not is_expense.startswith(_('n')):
                            print(_('Answer yes or no. Category was not created, try again.'))
                            continue
                        params.update({'category_id': add_category(data_store, params.get('category'), True if is_expense.startswith(_('y')) else False)})
                else:
                    params = None
                return params
        except IOError:
            pass
    return None


def format_balance_entry(entry):
    return {
        'timestamp': datetime.fromtimestamp(entry.get('timestamp'), timezone.utc).strftime("%Y-%m-%d"),
        'description': entry.get('description'),
        'amount': '{}{}'.format('-' if entry.get('cash_flow') == 'D' else '', str(entry.get('amount')))
    }


def int_val(value):
    return int(value * 100)


def do_review(args, data_store):
    amount_details = []
    no_category = data_store.get_category_by_name(_('No Category')).get('name')
    if not no_category:
        print(_("Nothing to review"))
        quit(0)
    for entry in data_store.get_balance_entries_by_amount_detail_category_name(_('No Category')):
        print('-' * 15)
        print("{timestamp} | {description} | {amount}".format(**format_balance_entry(entry)))
        print('-' * 15)
        current_amount = 0
        while int_val(current_amount) < int_val(entry.get('amount')):
            category_details = prompt_category(data_store)
            if not category_details:
                break
            amount_detail = {
                'category_id': category_details.get('category_id'),
                'amount': category_details.get('amount', entry.get('amount') - current_amount),
                'annotation': category_details.get('annotation', ''),
                'timestamp': entry.get('timestamp'),
                'balance_entry_id': entry.get('id'),
                'cash_flow': entry.get('cash_flow')
            }
            if int_val(amount_detail.get('amount') + current_amount) > int_val(entry.get('amount')):
                print(_('Balance entry amount exceeded'))
                continue
            current_amount += amount_detail.get('amount')
            diff = entry.get('amount') - current_amount
            if int_val(diff) != 0:
                print(f"{diff:.2f} remaining, please add a category to it.")
            amount_details.append(amount_detail)
        if not category_details:
            break

    unique_balance_entries = set([x.get('balance_entry_id') for x in amount_details])
    for balance_entry_id in unique_balance_entries:
        data_store.delete_all_amount_detail_by_balance_entry_id(balance_entry_id)

    data_store.create_amount_detail_items(amount_details)

    if len(unique_balance_entries) > 0:
        print(_("{count} records updated").format(count=len(unique_balance_entries)))
    else:
        print(_("Nothing changed"))
