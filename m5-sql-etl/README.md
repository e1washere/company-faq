# Mini ETL demo (M5)

*Creates staging table → transforms to final table → simple analytics query
with a window function.*
– see m5_etl_demo.sql
![Query result](../docs/m5_etl_result.png)

Key things shown:

| Step | Feature                             |
|------|-------------------------------------|
| 1    | `CREATE OR REPLACE TABLE … AS SELECT` with inline data |
| 2    | Window function `RANK() OVER(PARTITION BY … ORDER BY …)` |
| 3    | Final analytic `SELECT` + result grid |

