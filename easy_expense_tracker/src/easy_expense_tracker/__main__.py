from argparse import ArgumentParser
from . import extractor
from . import importer
from . import reviewer
from . import aggregator

import gettext

def import_failure_callback(data):
    if data.get("status") == importer.DUPLICATE_DATA_CSV_FILE_CODE:
        print(_("Warning: skipping duplicated data read from input file, fix it and run again: {entry}") \
            .format(entry=data.get("message")))


def import_success_callback(data):
    if data.get("status") == 0:
        print(_("{count} imported records").format(count = data.get("imported_records")))


if __name__ == "__main__":
    gettext.install("balance")
    parser = ArgumentParser(prog = "balance")

    subparsers = parser.add_subparsers(dest="command", help=_("sub-command help"))

    import_parser = subparsers.add_parser("import", help=_("import help"))
    import_parser.add_argument("--template", "-t", required=True, default="bank", help=_("Template for field extraction from csv file"))
    import_parser.add_argument("--due-date", help=_("Due date for credit card accounts"))
    import_parser.add_argument("--include-today", action='store_true', help=_("It causes the import process to include bank statement posts up to and including today's date"))
    import_parser.add_argument("CSV")

    review_parser = subparsers.add_parser("review", help=_("review help"))

    aggregator_parser = subparsers.add_parser("aggregate", help=_("aggregator help"))
    aggregator_parser.add_argument("--from-date", help=_("Begin of period of data to be aggregated ex. 2023-01 or current month if blank"))
    aggregator_parser.add_argument("--to-date", help=_("End of period to be aggregated ex. 2023-02 or current month if blank"))

    parser.add_argument("--database", "-d", required=True, help=_("Database"))

    args = parser.parse_args()

    if args.command == 'import':
        importer.do_import(extractor.get_extractor(args.template, args.CSV),
            args, import_success_callback, import_failure_callback)
    elif args.command == 'review':
        reviewer.do_review(args)
    elif args.command == 'aggregate':
        aggregator.do_aggregate(args)
        pass

