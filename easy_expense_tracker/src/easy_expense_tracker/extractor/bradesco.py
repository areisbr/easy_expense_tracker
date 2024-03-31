import csv
import locale

from datetime import datetime
from .extraction_result import ExtractionResult
from .util import should_generate_row

path : str = ""
template_name : str = "Bradesco"


def atof(value : str) -> float:
    if value == '' or value == None:
        return 0.0
    result = locale.atof(value)
    return result

def extract(args):
    cur_loc = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    for result in _extract(args):
        yield result
    locale.setlocale(locale.LC_ALL, cur_loc)
    
def begin_of_today_timestamp():
    return int(datetime.today().timestamp()) - int(datetime.today().timestamp()) % 86400

def _extract(args):
    dialect = csv.excel()
    dialect.delimiter=';'
    with open(path, encoding='iso-8859-1') as csvfile:
        next(csvfile)
        next(csvfile)
        data = csv.reader(csvfile, dialect)
        start_of_entry = False
        for row in data:
            if 'Últimos Lançamentos' in row:
                break
            if len(row) < 2 or row[1] == 'SALDO ANTERIOR':
                continue
            try:
                timestamp = datetime.strptime(row[0], "%d/%m/%y").timestamp();
                if not should_generate_row(timestamp, args.include_today):
                    continue
                start_of_entry = True
            except Exception:
                start_of_entry = False
            if start_of_entry == True:
                if len(row) < 6:
                    continue
                description = row[1].strip()
                doc_id = row[2]
                amount = max(abs(atof(row[3])), abs(atof(row[4])))
                if amount == 0:
                    continue;
                cash_flow = "C" if row[3] else "D"
                category = row[6] if len(row) > 6 else ''
                annotations = row[7] if len(row) > 7 else ''
                result = ExtractionResult(timestamp,
                        description,
                        abs(amount),
                        cash_flow,
                        doc_id,
                        category,
                        annotations,
                        template_name)
            else:
                if len(row) == 4 and result:
                    result.description += f" - {row[1]}"
                    yield result
