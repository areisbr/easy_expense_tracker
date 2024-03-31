WITH income AS (
	SELECT
		strftime('%Y-%m', be."timestamp", 'unixepoch') as year_month,
		SUM(ad.amount) as amount
	FROM
		balance_entries be
		JOIN amount_detail ad ON ad.balance_entry_id = be.id 
		JOIN categories c ON c.id = ad.category_id
	WHERE
		c.name IN (
			'Salário',
			'Estorno',
			'Vale Alimentação',
			'Resgate de Aplicação') AND
		strftime('%Y-%m', be."timestamp", 'unixepoch') = strftime('%Y-%m', 'now')
),
expenses AS (
	SELECT
		STRFTIME('%Y-%m',COALESCE(NULLIF(be.due_date, 0), be."timestamp"), 'unixepoch') as year_month,
		SUM(ad.amount) as amount
	FROM
		balance_entries be
		JOIN amount_detail ad ON ad.balance_entry_id = be.id 
		JOIN categories c ON c.id = ad.category_id
		JOIN bank_accounts ba ON ba.id = be.bank_account_id
	WHERE
		c.expense = TRUE AND (
			(strftime('%Y-%m', be."timestamp", 'unixepoch') = strftime("%Y-%m", 'now') AND
			ba.credit = FALSE) OR
			(strftime('%Y-%m', be.due_date, 'unixepoch') = strftime("%Y-%m", 'now') AND
			ba.credit = TRUE)
		)
)
SELECT
	coalesce(i.year_month, e.year_month) as Mês,
	coalesce(i.amount, 0.0) as Receitas,
	coalesce(e.amount, 0.0) as Despesas,
	coalesce(i.amount, 0.0) - coalesce(e.amount, 0.0) as Resultado
FROM
	income i
	FULL OUTER JOIN expenses e ON e.year_month = i.year_month

