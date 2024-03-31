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
		strftime('%Y-%m', be."timestamp", 'unixepoch') = "2023-12"
)
SELECT
	i.year_month,
	coalesce(sum(amount) filter(where i.category = 'Salary'), 0) as 'Salary',
	coalesce(sum(amount) filter(where i.category = 'Refund'), 0) as 'Refund',
	coalesce(sum(amount) filter(where i.category = 'Redemption'), 0) as 'Redemption',
	coalesce(sum(amount) filter(where i.category = 'Meal allowance'), 0) as 'Meal allowance'
FROM
	income i
