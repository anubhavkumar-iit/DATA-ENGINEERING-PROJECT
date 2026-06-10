# Data Model Justification

## Dataset Characteristics
- Total Records: 8,844,800
- Total Columns: 20
- Distinct Stations: 15
- Distinct Pollutants: 13
- Dataset is read-heavy and used for analytics and reporting

## Reason for Selecting Star Schema
1. Reduces redundancy by separating descriptive attributes into dimension tables.
2. Simplifies analytical queries by keeping facts and dimensions separate.
3. Optimized for OLAP workloads (aggregations, trends, filtering).
4. Supports faster reporting and dashboard generation.
5. Easy to maintain and extend for future use cases.

## Alternative Models Considered
- **Flat Table:** Rejected due to high redundancy.
- **MongoDB (Document):** Rejected because dataset has structured relationships and fixed schema.
- **Cassandra (Wide Column):** Rejected because workload is not write-intensive or distributed.
- **Snowflake Schema:** Rejected because additional normalization increases query complexity and joins, slowing analytics.

## Analytical Justification
- Millions of rows repeat the same station and pollutant data.
- Star Schema allows creating dimension tables for:
  - Time
  - Station
  - Pollutant
- Fact table contains measurements only, making queries like monthly averages or station comparisons efficient.

## Evidence from Queries
- Queries executed on the cleaned dataset (e.g., average pollutant by station or month) are simple and fast due to the dimensional model.
- Reduces storage for repeated descriptive attributes while preserving analytical efficiency.

## References
1. Kimball, R., & Ross, M. *The Data Warehouse Toolkit*, 3rd Edition.
2. Chaudhuri, S., & Dayal, U. "An Overview of Data Warehousing and OLAP Technology," *ACM SIGMOD*, 1997.
3. Star Schema Benchmark Research — demonstrates performance benefits for OLAP queries.