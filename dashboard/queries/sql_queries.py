# sql_queries.py
# Reusable SQL Query Layer for Air Quality Analytics Dashboard
# Connects to Milestones 2 and 3 by providing optimized OLAP aggregates.

# 1. Dashboard KPI summary metrics (from database)
KPI_TOTAL_MEASUREMENTS = """
SELECT COUNT(*) FROM fact_measurements;
"""

KPI_TOTAL_STATIONS = """
SELECT COUNT(*) FROM dim_station;
"""

KPI_TOTAL_POLLUTANTS = """
SELECT COUNT(*) FROM dim_pollutant;
"""

KPI_DATE_RANGE = """
SELECT MIN(dt_str), MAX(dt_str) FROM dim_time;
"""

# 2. Station analytics
STATION_AVERAGE_POLLUTANT = """
SELECT s.station_name, 
       ROUND(AVG(f.value), 2) AS avg_value,
       MIN(f.value) AS min_value,
       MAX(f.value) AS max_value,
       COUNT(f.value) AS reading_count
FROM fact_measurements f
JOIN dim_station s ON s.station_id = f.station_id
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
WHERE p.pollutant_name = ?
GROUP BY s.station_name
ORDER BY avg_value DESC;
"""

STATION_COMPARISON_ALL_POLLUTANTS = """
SELECT s.station_name, 
       p.pollutant_name, 
       ROUND(AVG(f.value), 2) AS avg_value
FROM fact_measurements f
JOIN dim_station s ON s.station_id = f.station_id
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
GROUP BY s.station_name, p.pollutant_name;
"""

# 3. Pollutant analytics
POLLUTANT_SUMMARY = """
SELECT p.pollutant_name,
       ROUND(AVG(f.value), 4) AS avg_value,
       ROUND(MIN(f.value), 4) AS min_value,
       ROUND(MAX(f.value), 4) AS max_value,
       COUNT(f.value) AS reading_count
FROM fact_measurements f
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
GROUP BY p.pollutant_name
ORDER BY avg_value DESC;
"""

POLLUTANT_RAW_DISTRIBUTION = """
SELECT f.value, s.station_name
FROM fact_measurements f
JOIN dim_station s ON s.station_id = f.station_id
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
WHERE p.pollutant_name = ? AND f.value IS NOT NULL;
"""

# 4. Time-series analytics
TIME_DAILY_TREND = """
SELECT t.day, 
       ROUND(AVG(f.value), 2) AS avg_value
FROM fact_measurements f
JOIN dim_time t ON t.time_id = f.time_id
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
WHERE p.pollutant_name = ?
GROUP BY t.day
ORDER BY t.day;
"""

TIME_HOURLY_TREND = """
SELECT t.hour, 
       ROUND(AVG(f.value), 2) AS avg_value
FROM fact_measurements f
JOIN dim_time t ON t.time_id = f.time_id
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
WHERE p.pollutant_name = ?
GROUP BY t.hour
ORDER BY t.hour;
"""

TIME_AQI_DISTRIBUTION = """
SELECT 
    CASE 
        WHEN f.value <= 50 THEN 'Good'
        WHEN f.value <= 100 THEN 'Moderate'
        WHEN f.value <= 200 THEN 'Poor'
        ELSE 'Severe'
    END AS aqi_category,
    COUNT(*) AS count
FROM fact_measurements f
JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
WHERE p.pollutant_name = 'pm25'
GROUP BY aqi_category;
"""

# 5. Station lists and Pollutant lists for filters
GET_ALL_STATIONS = """
SELECT station_id, station_name FROM dim_station;
"""

GET_ALL_POLLUTANTS = """
SELECT pollutant_id, pollutant_name FROM dim_pollutant;
"""

# 6. SQL showcase queries (Matching Milestone 2/3 queries)
SHOWCASE_QUERY_1 = """
-- Q1: Average Pollutant Value by Station (for PM2.5)
SELECT s.station_name,
       ROUND(AVG(f.value), 2) AS avg_pm25,
       ROUND(MIN(f.value), 2) AS min_pm25,
       ROUND(MAX(f.value), 2) AS max_pm25
FROM   fact_measurements f
JOIN   dim_station   s ON s.station_id   = f.station_id
JOIN   dim_pollutant p ON p.pollutant_id = f.pollutant_id
WHERE  p.pollutant_name = 'pm25'
GROUP  BY s.station_name
ORDER  BY avg_pm25 DESC;
"""

SHOWCASE_QUERY_2 = """
-- Q2: Hourly Average Temperature per Station
SELECT t.hour, 
       s.station_name, 
       ROUND(AVG(f.at_c), 2) AS avg_temp_c
FROM   fact_measurements f
JOIN   dim_station s ON s.station_id = f.station_id
JOIN   dim_time    t ON t.time_id    = f.time_id
WHERE  f.at_c IS NOT NULL
GROUP  BY t.hour, s.station_name
ORDER  BY t.hour, s.station_name
LIMIT  50;
"""

SHOWCASE_QUERY_3 = """
-- Q3: Pollutant Measurement Counts and Missing Data Completeness
SELECT p.pollutant_name,
       COUNT(*) AS total_readings,
       SUM(CASE WHEN f.value IS NULL THEN 1 ELSE 0 END) AS null_count,
       ROUND((SUM(CASE WHEN f.value IS NULL THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS null_percentage
FROM   fact_measurements f
JOIN   dim_pollutant p ON p.pollutant_id = f.pollutant_id
GROUP  BY p.pollutant_name 
ORDER  BY total_readings DESC;
"""
