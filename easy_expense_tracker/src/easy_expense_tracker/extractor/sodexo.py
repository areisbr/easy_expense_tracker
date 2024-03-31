from datetime import datetime
from io import StringIO
from .extraction_result import ExtractionResult
from .util import should_generate_row

import csv

path = ""
template_name = "Sodexo"

CREDIT_DESCRIPTIONS = [
    "DISPONIBILIZACAO DE VALOR",
    "DISPONIBILIZACAO DE BENEFICIO ONLINE (CREDITO)"
]


def extract(args):
    dialect = csv.excel()
    dialect.delimiter=';'
    dialect = dialect

    csvfile = StringIO()
    with open(path, encoding="iso-8859-1") as input_f:
        csvfile.write(input_f.read())
        csvfile.seek(0)

    for i in range(8):
        next(csvfile)
    data = csv.reader(csvfile, dialect)
    for row in data:
        if len(row) < 3:
            break
        timestamp = datetime.strptime(row[0], "%d/%m/%Y").timestamp();
        if not should_generate_row(timestamp, args.include_today):
            continue
        description = row[1].strip()
        amount = float(row[2].replace(',','.'))
        cash_flow = "C" if description in CREDIT_DESCRIPTIONS else "D"
        category = row[3] if len(row) > 3 else ""
        annotations = row[4] if len(row) > 4 else ""
        doc_id = ""
        yield ExtractionResult(timestamp, description, abs(amount), cash_flow, doc_id, category, annotations, template_name)
