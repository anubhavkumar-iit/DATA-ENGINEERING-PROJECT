# Literature Review Supporting the Selected Data Model

## 1. Kimball & Ross – The Data Warehouse Toolkit

Kimball and Ross advocate the use of dimensional modeling and Star Schemas for analytical workloads. They argue that Star Schemas simplify query design, improve understandability, and provide efficient aggregation for business intelligence applications.

**Relevance to our project:**
Our air quality dataset contains millions of measurements that are repeatedly analyzed by station, pollutant, and time. The Star Schema provides an intuitive structure for these analytical queries.



## 2. Chaudhuri & Dayal (1997) – An Overview of Data Warehousing and OLAP Technology

This paper discusses the role of data warehouses in supporting analytical workloads and highlights multidimensional data models as a foundation for efficient OLAP operations.

**Relevance to our project:**
The project requires aggregation and trend analysis over 8.8 million records. A dimensional model aligns well with these OLAP-style queries.



## 3. Star Schema Benchmark (O'Neil et al.)

The Star Schema Benchmark demonstrates that dimensional schemas are highly effective for analytical workloads involving filtering, grouping, and aggregation.

**Relevance to our project:**
Typical project queries such as average pollutant concentration by station or monthly pollutant trends match the benchmark's analytical workload characteristics.



## 4. Inmon – Building the Data Warehouse

Inmon emphasizes the importance of organizing data for decision support and analytical processing rather than transactional processing.

**Relevance to our project:**
The air quality dataset is used primarily for analysis and reporting, making a warehouse-oriented dimensional design appropriate.



## Conclusion

The literature consistently supports dimensional modeling and Star Schemas for large-scale analytical datasets. Given the project's analytical query patterns, large record count, and repeated descriptive attributes, the Star Schema is the most suitable data model.
