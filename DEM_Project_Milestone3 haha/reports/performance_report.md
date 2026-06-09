# Performance Evaluation

## Transformation Pipeline

The batch transformation workflow consisted of the following stages:

1. Load partitioned parquet dataset into Spark.
2. Perform data profiling and missing value analysis.
3. Apply data cleaning and imputation rules.
4. Generate transformed analytical dataset.
5. Validate data quality improvements.
6. Store cleaned output for downstream analytical processing.


## Query 1: Average Pollutant Value by Station

Purpose: Compare air quality measurements across monitoring stations.

Result:
The query successfully aggregated pollutant measurements by station and returned analytical insights suitable for reporting.

## Query 2: Average Pollutant Value by Pollutant Type

Purpose: Compare pollutant behavior across pollutant categories.

Result:
The query efficiently aggregated measurements by pollutant and provided useful environmental insights.

## Query 3: Monthly Trend Analysis

Purpose: Observe temporal trends in air quality measurements.

Result:
The query aggregated millions of records by year and month, demonstrating the suitability of the dimensional model for trend analysis.

## Conclusion

The transformed dataset supports analytical workloads involving aggregation, filtering, grouping, and trend analysis. These workloads align with the intended use of a Star Schema and justify the selected data model.

## Impact of Data Cleaning

The cleaning pipeline removed invalid, duplicate, and inconsistent records from the dataset. This improved the reliability of analytical queries and reduced the risk of misleading insights.

### Benefits

- Improved query accuracy
- More consistent pollutant measurements
- Better aggregation results
- Reduced noise in analytical reporting

## End User Benefits

The cleaned dataset enables environmental agencies and researchers to make more reliable decisions based on air quality trends. Dashboards built on top of the warehouse can provide trustworthy pollution statistics and historical comparisons.


## Query Performance Analysis

The dimensional model simplified analytical queries by reducing the need for repeated descriptive attributes in the fact table.

Observed benefits:

- Faster aggregation queries on pollutant measurements
- Simpler filtering by station and pollutant dimensions
- Improved readability of analytical SQL queries
- Better support for dashboard-oriented workloads

## Analytical Insights

The warehouse structure enables efficient generation of:

- Monthly pollution trends
- Station-wise pollutant comparisons
- Pollutant contribution analysis
- Historical trend reporting

## Data Quality Validation

Validation checks performed:

- Null value detection
- Duplicate record identification
- Schema consistency verification
- Dimension key validation

These checks improve confidence in downstream analytics and reporting.

## Data Quality Validation

Several validation checks were performed after data cleaning:

- Missing value detection and treatment
- Duplicate record analysis
- Schema consistency verification
- Foreign key validation between fact and dimension tables

These checks improve confidence in analytical reporting and downstream decision-making.

## Relevance to Project Design

The reviewed literature supports the use of dimensional modeling for analytical workloads. The selected star schema reduces query complexity while improving reporting efficiency for large datasets.

The findings also support the use of batch data cleaning and preprocessing before warehouse loading to improve data quality.


## Spark Configuration

| Parameter          | Value        |
| ------------------ | ------------ |
| Executor Memory    | ACTUAL_VALUE |
| Driver Memory      | ACTUAL_VALUE |
| Shuffle Partitions | ACTUAL_VALUE |

## Transformation Pipeline

1. Load partitioned parquet dataset
2. Profile missing values and data quality issues
3. Perform batch data cleaning and imputation
4. Generate derived features
5. Write cleaned dataset for analytical processing

## Execution Time Benchmarks

| Stage               | Execution Time (seconds) |
| ------------------- | ------------------------ |
| Data Loading        | ACTUAL_VALUE             |
| Data Profiling      | ACTUAL_VALUE             |
| Data Cleaning       | ACTUAL_VALUE             |
| Feature Engineering | ACTUAL_VALUE             |
| Output Write        | ACTUAL_VALUE             |
| Total Pipeline Time | ACTUAL_VALUE             |

### Benchmark Summary

The Spark pipeline successfully processed the air quality dataset and produced a cleaned analytical dataset suitable for warehouse loading and reporting.
