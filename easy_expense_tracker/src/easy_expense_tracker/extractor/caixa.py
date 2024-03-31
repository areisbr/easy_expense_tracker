import csv

from datetime import datetime
from .extraction_result import ExtractionResult
from .util import should_generate_row

path : str = ""
template_name : str = "Caixa"

def extract(args):
    dialect = csv.excel()
    dialect.delimiter=';'
    with open(path) as csvfile:
        next(csvfile)
        data = csv.reader(csvfile, dialect)
        for row in data:
            if len(row) < 6:
                break
            doc_id = row[2]
            amount = float(row[4])
            if amount == 0:
                continue;
            timestamp = datetime.strptime(row[1], "%Y%m%d").timestamp();
            if not should_generate_row(timestamp, args.include_today):
                continue
            cash_flow = row[5]
            description = row[3]
            category = '' if len(row) < 7 else row[6]
            annotations = '' if len(row) < 9 else row[8]
            yield ExtractionResult(timestamp, description, abs(amount), cash_flow, doc_id, category, annotations, template_name)
