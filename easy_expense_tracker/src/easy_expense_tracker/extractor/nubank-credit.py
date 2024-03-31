import csv

from datetime import datetime
from .extraction_result import ExtractionResult
from .util import should_generate_row

path = ""
template_name = "Nubank Crédito"

def extract(args):
    if not args.due_date:
        user_input = input(_('Due date (ex. YYYY-MM-DD): '))
        args.due_date = user_input

    dialect = csv.excel()
    dialect.delimiter=','
    with open(path) as csvfile:
        next(csvfile)
        data = csv.reader(csvfile, dialect)
        for row in data:
            if len(row) < 4:
                break
            timestamp = datetime.strptime(row[0], "%Y-%m-%d").timestamp();
            if not should_generate_row(timestamp, args.include_today):
                continue
            description = row[2]
            amount = float(row[3])
            cash_flow = "D" if amount > 0 else "C" # cartão de crédito é invertido em relação a conta corrente
            category = row[4] if len(row) > 4 else ""
            annotations = row[5] if len(row) > 5 else ""
            doc_id = ""
            yield ExtractionResult(timestamp, description, abs(amount), cash_flow, doc_id, category, annotations, template_name)
