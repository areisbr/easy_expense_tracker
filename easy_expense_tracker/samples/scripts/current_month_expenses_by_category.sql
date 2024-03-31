SELECT
	c.name AS Category,
	printf('%.2f', SUM(ad.amount)) AS Amount
FROM
	balance_entries be
	JOIN amount_detail ad ON ad.balance_entry_id = be.id
	JOIN categories c ON c.id = ad.category_id
	JOIN bank_accounts ba ON ba.id = be.bank_account_id 
WHERE
	c.expense = TRUE AND (
		(strftime('%Y-%m', be."timestamp", 'unixepoch') = "2023-12" AND ba.credit = FALSE) OR
		(strftime('%Y-%m', be.due_date, 'unixepoch') = "2023-12" AND ba.credit = TRUE)
	)
GROUP BY
	c.name
ORDER BY
	SUM(ad.amount) DESC
