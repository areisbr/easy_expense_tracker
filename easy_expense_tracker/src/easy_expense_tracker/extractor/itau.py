from datetime import datetime
from .extraction_result import ExtractionResult
from .util import should_generate_row

import csv

path = ""
template_name = "Itau"

def extract(args):
    dialect = csv.excel()
    dialect.delimiter=';'
    dialect = dialect
    with open(path) as csvfile:
        data = csv.reader(csvfile, dialect)
        for row in data:
            if len(row) < 3:
                break
            timestamp = datetime.strptime(row[0], "%d/%m/%Y").timestamp();
            if not should_generate_row(timestamp, args.include_today):
                continue
            description = row[1]
            amount = float(row[2].replace(',','.'))
            cash_flow = "C" if amount > 0 else "D"
            category = row[3] if len(row) > 3 else ""
            annotations = row[4] if len(row) > 4 else ""
            doc_id = ''
            yield ExtractionResult(timestamp, description, abs(amount), cash_flow, doc_id, category, annotations, template_name)
