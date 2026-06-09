# verify_setup.py
# Verification script to test DB connection and module imports

import sys
import os
from pathlib import Path

# Add parent dir to path
sys.path.append(str(Path(__file__).resolve().parent))

def run_tests():
    print("=== Testing Module Imports ===")
    try:
        from utils.db_connector import find_db_path, get_connection, validate_warehouse_tables, run_query
        import queries.sql_queries as qy
        print("✓ Successfully imported db_connector and sql_queries modules.")
    except Exception as e:
        print(f"✗ Import error: {str(e)}")
        return False

    print("\n=== Testing Database Auto-Discovery ===")
    try:
        db_path = find_db_path()
        print(f"✓ Located SQLite DB at: {db_path}")
        print(f"✓ Database size: {os.path.getsize(db_path) / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"✗ DB discovery error: {str(e)}")
        return False

    print("\n=== Testing Database Connection & WAL mode ===")
    try:
        conn = get_connection()
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        print(f"✓ Connection successful. SQLite journal mode: {journal_mode}")
        conn.close()
    except Exception as e:
        print(f"✗ Connection error: {str(e)}")
        return False

    print("\n=== Testing Table Schema Integrity ===")
    try:
        validation = validate_warehouse_tables()
        all_ok = True
        for table, info in validation.items():
            if info["exists"]:
                print(f"✓ Table '{table}': EXISTS ({info['row_count']:,} rows, {len(info['columns'])} columns)")
            else:
                print(f"✗ Table '{table}': MISSING OR ERROR. Details: {info.get('error', 'Does not exist')}")
                all_ok = False
        if not all_ok:
            return False
    except Exception as e:
        print(f"✗ Table validation error: {str(e)}")
        return False

    print("\n=== Testing SQL Showcase Queries Execution ===")
    try:
        df1 = run_query(qy.SHOWCASE_QUERY_1)
        print(f"✓ Query 1 executed. Returned {len(df1)} rows.")
        df2 = run_query(qy.SHOWCASE_QUERY_2)
        print(f"✓ Query 2 executed. Returned {len(df2)} rows.")
        df3 = run_query(qy.SHOWCASE_QUERY_3)
        print(f"✓ Query 3 executed. Returned {len(df3)} rows.")
    except Exception as e:
        print(f"✗ SQL Execution error: {str(e)}")
        return False

    print("\n=== Testing Regional Analytics Query ===")
    try:
        regional_q = """
        SELECT f.station_id, s.station_name, p.pollutant_name,
               ROUND(AVG(f.value), 2) AS avg_value
        FROM fact_measurements f
        JOIN dim_station s ON s.station_id = f.station_id
        JOIN dim_pollutant p ON p.pollutant_id = f.pollutant_id
        WHERE p.pollutant_name = 'pm25'
        GROUP BY f.station_id, s.station_name, p.pollutant_name;
        """
        df_reg = run_query(regional_q)
        print(f"✓ Regional query executed. Returned {len(df_reg)} rows across {df_reg['station_id'].nunique()} stations.")
    except Exception as e:
        print(f"✗ SQL Execution error: {str(e)}")
        return False

    print("\n=== SETUP VERIFICATION COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
