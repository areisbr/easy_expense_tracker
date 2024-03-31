
Easy Expense Tracker
====================

Easy Expense Tracker is a straightforward tool designed to import and consolidate account statements from various financial services into an SQL-compatible database. Before you begin, export the CSV file from your checking account, credit card, or food allowance card, then you are ready to proceed. Please ensure that each CSV file contains the statements from a single account.

The tool is compatible with CSV files from a range of financial services. If your service is not listed below, refer to the instructions in the section [Adding a New Template](#adding-a-new-template) of this document, or provide me with a sample file, and I will be happy to include a new template in a future release.

- Bradesco
- Caixa Econômica Federal
- Itau
- Nubank (Credit Card)
- Nubank (Debit)
- Sodexo (Pluxee Beneficios)

You might wish to review the imported records, categorize them, split the amount into multiple categories, or add detailed annotations. The review is an optional step and does not interrupt the importing process.

Splitting records into multiple categories can be particularly useful, for example, when a colleague does a check splitting and will reimburse you later. During a review session, you can specify their portion in an incoming category (e.g., reimbursements) and your portion in an expense category (e.g., *meals*).

Use the *aggregate* command to generate a monthly total of expenses by category on a table called *monthly_expenses_by_category*. This step is also optional and does not interrupt the importing process.


Quick Start
===========

```shell
# Install
pip3 install easy_expense_tracker

# Import data to a SQLite database from a CSV file (e.g., itau.csv in samples directory)
python3 -m easy_expense_tracker -d test.db import --template itau itau.csv

# Review uncateorized items (optional step)
python3 -m easy_expense_tracker -d test.db review

# Generate a monthly total of expenses by category on the table monthly_expenses_by_category (optional step)
python3 -m easy_expense_tracker -d test.db aggregate --from-date 2023-01 --to-date 2023-12
```


Adding a New Template
=====================

A template is a small piece of code used to read CSV files. They are used to abstract the data format provided by the service which provided them. Use the `ExtractionResult` interface to deliver the data read from CSV to the importing process. Place your newly created template into the *extractor* directory in the root directory of this Python module.


```python
# timestamp : timestamp in unix epoch format
# description : record description
# amount : absolute amount value, use cash_flow to if record express debits as a negative amount
# cash_flow : use 'C' for credit or 'D' for debit
# doc_id : some bank statements may include this field, use an empty string if not
# category : record category
# annotations : record annotations
# template_name : which template name this record belongs to

ExtractionResult(timestamp, description, amount, cash_flow, doc_id, category, annotations, template_name)

```

