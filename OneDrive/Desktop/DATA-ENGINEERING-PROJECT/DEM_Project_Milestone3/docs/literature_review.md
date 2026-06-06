# Literature Review Supporting the Selected Data Model

<!-- anchor: intro -->
## Introduction

This review examines the academic and technical literature that informed the data modelling decisions made in this project. The Delhi air quality dataset contains 8.8 million rows spanning 15 monitoring stations, 13 pollutant types, and hourly readings over multiple years. The literature consistently points to dimensional modelling and Star Schemas as the most appropriate design for this class of analytical workload.

---

<!-- anchor: theme-dimensional -->
## Theme 1 — Dimensional Modelling as the Foundation for Analytical Systems

**Kimball & Ross — The Data Warehouse Toolkit**

Kimball and Ross established dimensional modelling as the standard approach for analytical data systems. They argue that Star Schemas simplify query design, improve understandability, and deliver efficient aggregation for business intelligence applications.

*Relevance:* Our dataset has clear, repeated descriptive attributes — station name, city, state, pollutant type — that repeat across millions of fact rows. Normalising these into dimension tables (`dim_station`, `dim_pollutant`, `dim_time`) directly follows Kimball's prescription and eliminates update anomalies.

**Inmon — Building the Data Warehouse**

Inmon emphasises organising data for decision support and analytical processing rather than transactional processing, arguing that warehouse-oriented design improves long-term maintainability.

*Relevance:* The air quality dataset is used purely for analysis and reporting — no transactional writes after ingestion. A warehouse-oriented design is therefore the correct choice.

---

<!-- anchor: theme-olap -->
## Theme 2 — OLAP Query Patterns and Multidimensional Models

**Chaudhuri & Dayal (1997) — An Overview of Data Warehousing and OLAP Technology**

This foundational paper discusses the role of data warehouses in supporting analytical workloads and highlights multidimensional data models as the basis for efficient OLAP operations including roll-up, drill-down, slice, and dice.

*Relevance:* The three core analytical queries in this project — average pollutant by station, average by pollutant type, and monthly trend analysis — are classic OLAP GROUP BY patterns. The dimensional model maps directly to these operations.

---

<!-- anchor: theme-benchmark -->
## Theme 3 — Empirical Evidence for Star Schema Performance

**Star Schema Benchmark — O'Neil et al.**

The Star Schema Benchmark provides empirical evidence that dimensional schemas outperform normalised schemas for analytical workloads involving filtering, grouping, and aggregation across large fact tables.

*Relevance:* Queries such as average pollutant concentration by station or monthly pollutant trends across 8.8 million records match the benchmark's workload characteristics. The benchmark supports the choice of SQLite star schema over a flat denormalised table or a document store.

---

<!-- anchor: conclusion -->
## Conclusion

The literature reviewed here converges on a single recommendation: for large-scale, read-heavy, multi-dimensional analytical datasets, the Star Schema dimensional model is the most suitable design. Given the project's 8.8 million fact rows, fixed station and pollutant vocabularies, and GROUP BY-heavy query patterns, this design is both theoretically justified and empirically validated.


