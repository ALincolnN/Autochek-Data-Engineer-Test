
-- The operations below have been done on PostgreSQL Version 14.7 on the PgAdmin4 Version 8.0 desktop application interface

-- ========================
-- SECTION: 1
-- ========================
CREATE TABLE borrower_table
	(borrower_id VARCHAR PRIMARY KEY, state VARCHAR, city VARCHAR, zip_code VARCHAR, borrower_credit_score VARCHAR);
	
CREATE TABLE loan_table
	(loan_id VARCHAR PRIMARY KEY, borrower_id VARCHAR, date_of_release DATE, term INT, interest_rate FLOAT4, 
	loan_amount BIGINT, down_payment BIGINT, payment_frequency FLOAT4, maturity_date DATE, 
	 FOREIGN KEY(borrower_id) REFERENCES borrower_table(borrower_id)
	);
	
CREATE TABLE payment_schedule
	(schedule_id VARCHAR, loan_id VARCHAR, expected_payment_amount FLOAT4, expected_payment_date DATE, 
	 FOREIGN KEY(loan_id) REFERENCES loan_table(loan_id));
	
CREATE TABLE loan_repayment
	(payment_id VARCHAR, loan_id VARCHAR, amount_paid FLOAT4, date_paid DATE, 
	 FOREIGN KEY(loan_id) REFERENCES loan_table(loan_id));
	 
	 
-- ========================
-- SECTION: 2
-- ======================== 
SELECT t1.borrower_id, t2.loan_id, t2.loan_amount, t2.date_of_release, t2.maturity_date, t2.interest_rate, t2.term, LEAD(t4.date_paid) OVER(PARTITION BY t4.loan_id ORDER BY t4.date_paid) - t4.date_paid as payment_frequency, t2.down_payment,
	t3.expected_payment_amount, t3.expected_payment_date, t4.amount_paid, t4.date_paid
FROM borrower_table AS t1
INNER JOIN loan_table AS t2 ON t1.borrower_id = t2.borrower_id
LEFT JOIN payment_schedule AS t3 ON t2.loan_id = t3.loan_id
LEFT JOIN loan_repayment AS t4 ON t3.loan_id = t4.loan_id
ORDER BY borrower_id, loan_id, loan_amount DESC

-- ========================
-- SECTION: 3
-- ========================
-- Missed payments
WITH expected_payments AS (
	SELECT loan_id, COUNT(*)
	FROM payment_schedule
	GROUP BY loan_id
),
payments_made AS (
	SELECT loan_id, COUNT(*)
	FROM loan_repayment
	GROUP BY loan_id
)
SELECT t1.borrower_id, t2.loan_id, (t3.count - t4.count) AS missed_payments
FROM borrower_table t1
INNER JOIN loan_table t2 ON t1.borrower_id = t2.borrower_id
INNER JOIN expected_payments AS t3 ON t2.loan_id = t3.loan_id
LEFT JOIN payments_made AS t4 ON t2.loan_id = t4.loan_id
ORDER BY t1.borrower_id, t2.loan_id

-- ========================
-- SECTION: 4
-- ========================
-- Selecting only the most recent record of loan_repayment data
WITH repayment_data AS (
	SELECT loan_id, amount_paid, date_paid
	FROM (
			SELECT *, ROW_NUMBER() OVER(PARTITION BY loan_id ORDER BY date_paid DESC) AS row_num
			FROM loan_repayment
		 ) AS partitioned_data
	WHERE partitioned_data.row_num = 1
),
-- Selecting only the most recent record of payment_schedule data
schedule_data AS (
	SELECT loan_id, expected_payment_amount, expected_payment_date
	FROM (
			SELECT *, ROW_NUMBER() OVER(PARTITION BY loan_id ORDER BY expected_payment_date DESC) AS row_num
			FROM payment_schedule
		 ) AS partitioned_data
	WHERE partitioned_data.row_num = 1
)
-- Joining the data from loan_table, borrower_table and previously generated Common Table Expressions and making calculations to produce desired results.
SELECT t1.city, t1.zip_code, t2.payment_frequency, t2.maturity_date, (t3.date_paid - t4.expected_payment_date) AS current_days_past_due, 
	t4.expected_payment_date AS last_due_date, t3.date_paid AS last_repayment_date, (t4.expected_payment_amount - t3.amount_paid) AS amount_at_risk
FROM borrower_table AS t1
INNER JOIN loan_table AS t2 ON t1.borrower_id = t2.borrower_id
LEFT JOIN repayment_data AS t3 ON t2.loan_id = t3.loan_id
LEFT JOIN schedule_data AS t4 ON t2.loan_id = t4.loan_id;
	 