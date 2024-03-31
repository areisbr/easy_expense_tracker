import csv

from datetime import datetime
from .extraction_result import ExtractionResult
from .util import should_generate_row


path = ""
template_name = "Nubank"

def extract(args):
    dialect = csv.excel()
    dialect.delimiter=','
    with open(path) as csvfile:
        next(csvfile)
        data = csv.reader(csvfile, dialect)
        for row in data:
            if len(row) < 4:
                break
            timestamp = datetime.strptime(row[0], "%d/%m/%Y").timestamp();
            if not should_generate_row(timestamp, args.include_today):
                continue
            doc_id = row[2]
            description = row[3]
            amount = float(row[1])
            cash_flow = "C" if amount > 0 else "D"
            category = row[4] if len(row) > 4 else ""
            annotations = row[5] if len(row) > 5 else ""
            yield ExtractionResult(timestamp, description, abs(amount), cash_flow, doc_id, category, annotations, template_name)
