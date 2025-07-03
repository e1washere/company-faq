-- 1) staging
CREATE OR REPLACE TABLE `patrianna-rag-demo.patrianna_demo.stg_employees` AS
SELECT * FROM UNNEST([
  STRUCT(1 AS emp_id,'Alice' AS full_name,'Data'    AS dept, 70000 AS salary, DATE '2024-02-01' AS hired_at),
  STRUCT(2,'Bob',   'Product',88000, DATE '2023-11-15'),
  STRUCT(3,'Carol', 'AI/ML', 105000, DATE '2024-04-20'),
  STRUCT(4,'Dylan', 'AI/ML',  98000, DATE '2023-07-01')
]);

-- 2) final table + window function
CREATE OR REPLACE TABLE `patrianna-rag-demo.patrianna_demo.employees` AS
SELECT
  *,
  RANK() OVER(PARTITION BY dept ORDER BY salary DESC) AS rank_in_dept
FROM `patrianna-rag-demo.patrianna_demo.stg_employees`;

-- 3) analysis query you screenshotted
SELECT dept, full_name, salary, rank_in_dept
FROM   `patrianna-rag-demo.patrianna_demo.employees`
ORDER  BY dept, rank_in_dept;