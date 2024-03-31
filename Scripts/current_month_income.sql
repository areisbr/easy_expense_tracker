WITH income AS (
	SELECT
		strftime('%Y-%m', be."timestamp", 'unixepoch') as year_month,
		c.name category,
		ad.amount as amount
	FROM
		balance_entries be
		JOIN amount_detail ad ON ad.balance_entry_id = be.id 
		JOIN categories c ON c.id = ad.category_id
	WHERE
		c.expense = FALSE AND
		strftime('%Y-%m', be."timestamp", 'unixepoch') = strftime('%Y-%m', 'now')
)
SELECT
	i.year_month,
	coalesce(sum(amount) filter(where i.category = 'Salário'), 0) as 'Salário',
	coalesce(sum(amount) filter(where i.category = 'Estorno'), 0) as 'Estorno',
	coalesce(sum(amount) filter(where i.category = 'Resgate de Aplicação'), 0) as 'Resgate de Aplicação',
	coalesce(sum(amount) filter(where i.category = 'Vale Alimentação'), 0) as 'Vale Alimentação'
FROM
	income i
