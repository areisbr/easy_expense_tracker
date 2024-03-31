SELECT
	strftime('%Y-%m-%d', be."timestamp", 'unixepoch') as "Data",
	ba.name as Banco,
	be.description as Descrição,
	ad.amount as Valor,
	c.name as Categoria,
	ad.annotation as Anotações
FROM
	balance_entries be
	JOIN amount_detail ad ON ad.balance_entry_id = be.id
	JOIN categories c ON c.id = ad.category_id
	JOIN bank_accounts ba ON ba.id = be.bank_account_id 
WHERE
	c.expense = TRUE AND (
		(strftime('%Y-%m', be."timestamp", 'unixepoch') = strftime("%Y-%m", 'now') AND ba.credit = FALSE) OR
		(strftime('%Y-%m', be.due_date, 'unixepoch') = strftime("%Y-%m", 'now') AND ba.credit = TRUE)
	)
ORDER BY
	"Data" ASC
