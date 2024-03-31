from hashlib import sha256
from datetime import datetime, timezone

DUPLICATE_DATA_CSV_FILE_CODE = 100

def get_category(name):
    default_category = _('No Category')
    return name if name else default_category


def get_bank_account(name, credit, data_store):
    return {
        "name": name,
        "credit": credit
    }


def get_due_date(args):
    due_date = 0
    if args.due_date:
        due_date = datetime.strptime(args.due_date, '%Y-%m-%d').timestamp()
    return due_date


def create_sha256_digest(entry):
    encoded = ''.join((
        entry.get("bank_account").get('name'),
        entry.get("description"),
        entry.get("doc_id"),
        str(entry.get("timestamp")),
        str(entry.get("amount"))
    )).encode('utf-8')
    return sha256(encoded).hexdigest()


def is_duplicate(entry, data_store):
    digest = entry.get("digest")
    result = data_store.get_balance_entry_by_digest(digest)
    return True if result and result.get('digest') == digest else False


def is_duplicate_digest_list(digest_list : list, entry : dict) -> bool:
    digest = entry.get("digest")
    return True if digest in digest_list else False


def get_amount_detail(timestamp, amount, category, annotation, data_store):
    return [{"timestamp": timestamp, "amount": amount, "category": get_category(category), "annotation": annotation}]


def do_import(extract_fun, args, data_store, success_fun, error_fun):
    import_count = 0
    digest_list = []
    for result in extract_fun(args):
        entry = {
            "bank_account": get_bank_account(result.template, args.due_date != None, data_store),
            "timestamp": result.timestamp,
            "amount": result.amount,
            "amount_detail": get_amount_detail(result.timestamp, result.amount, result.category, result.annotation, data_store),
            "doc_id": result.doc_id if result.doc_id else '',
            "description": result.description,
            "cash_flow": result.cash_flow.upper(),
            "due_date": get_due_date(args)
        }
        entry.update({"digest": create_sha256_digest(entry)})

        if is_duplicate_digest_list(digest_list, entry):
            error_fun({
                "status": DUPLICATE_DATA_CSV_FILE_CODE,
                "message": str(result)
            })
            continue
        else:
            digest_list.append(entry.get("digest"))

        if is_duplicate(entry, data_store):
            continue

        data_store.create_balance_entry(entry)
        import_count += 1
    success_fun({
        "status": 0,
        "imported_records": import_count
    })
