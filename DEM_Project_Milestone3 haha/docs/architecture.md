# Architecture and Data Serving Design

## System Architecture

Raw Air Quality Data
→ Spark Ingestion Pipeline
→ Partitioned Parquet Storage
→ Spark Data Profiling
→ Batch Data Cleaning
→ Feature Engineering
→ Cleaned Data Layer
→ Star Schema Data Warehouse
→ Analytical Queries
→ End Users

## Tools Used

### Apache Spark

Used for:

* Reading large parquet datasets
* Data profiling
* Batch transformations
* Cleaning operations
* Feature engineering

### Parquet

Used because:

* Columnar storage format
* Efficient compression
* Fast analytical reads
* Suitable for large datasets

### SQLite Data Warehouse

Used for:

* Structured storage
* Star schema implementation
* Analytical query execution

### Git

Used for:

* Version control
* Branch management
* Tracking milestone progress
* Collaborative development

## End User Use Cases

1. Compare pollutant levels across stations.
2. Analyze monthly air quality trends.
3. Study pollutant behavior over time.
4. Generate environmental monitoring reports.
5. Support decision-making using aggregated analytics.

## Data Serving

The cleaned and transformed dataset is stored in a warehouse-friendly structure that supports aggregation and reporting queries. Users interact with analytical views rather than raw data, improving performance and usability.

## Data Flow

1. Raw Air Quality Dataset (Parquet)
2. Spark Ingestion Pipeline
3. Data Profiling and Quality Assessment
4. Batch Data Cleaning
5. Feature Engineering
6. Star Schema Warehouse
7. Analytical Queries
8. End User Dashboards and Reports

## Real-World Usage

The cleaned and transformed dataset can be used by:

- Environmental agencies to monitor pollution trends.
- City planners to identify high-risk locations.
- Researchers analyzing air quality patterns.
- Public dashboards showing pollutant levels over time.
- Policy makers evaluating environmental interventions.

## Example Business Questions

1. Which station recorded the highest average pollutant concentration?
2. How do pollution levels vary across months?
3. Which pollutants contribute most to poor air quality?
4. Which locations show improving or worsening trends?
