"""
Milestone 3: Data Model (Clean) — Delhi Air Quality Dataset
=====================================================
Database Choice: SQLite (Relational / RDBMS)
Schema Style:  Star Schema (Dimensional Model)

WHY RDBMS (SQLite)?
--------------------
Our dataset has clear, well-defined relationships:
  - Stations are fixed entities (15 stations, stable attributes: name, city, state)
  - Pollutants are a fixed controlled vocabulary (13 types)
  - Every measurement row is a FACT that references a station, a pollutant, and a time

The data is:
  ✓ Structured with consistent column types (no nested / variable schema)
  ✓ Relatively narrow (22 cols) — not a wide-column use case
  ✓ Fully relational — station info repeats millions of times → normalise it out
  ✓ Needs SQL queries (GROUP BY station, pollutant, time → classic OLAP pattern)
  ✓ ~8.8M rows is manageable in SQLite for analytics; no distributed infra needed

CHANGES FROM MILESTONE 2
  - Ingests cleaned data: negative values dropped, weather NULLs imputed
  - Outputs to air_quality_clean.db (original air_quality.db untouched)
  - Indexes built after loading for faster ingestion
  - MAX_FILES = None to load all 192 partitions

USAGE
-----
    python scripts/data_model_clean.py
"""

import sqlite3, pandas as pd, glob, re, logging
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(r"C:\Users\User\OneDrive\Desktop\DATA-ENGINEERING-PROJECT\DEM_Project_Milestone3")
PARQUET_DIR = Path(r"C:\Users\User\OneDrive\Desktop\DATA-ENGINEERING-PROJECT\DEM_Project_Milestone1\DEM_Project_Milestone1\data\ingestion_layer\ingestion_layer\ingestion_layer\partitioned_data")
DB_PATH     = BASE_DIR / "data" / "database" / "air_quality_clean.db"
LOG_PATH    = BASE_DIR / "logs" / "data_model_clean_logs.txt"
MAX_FILES   = None

WEATHER_COLS = ["at_c", "rh_percent", "ws_m_s", "wd_deg",
                "rf_mm", "tot_rf_mm", "sr_w_mt2", "bp_mmhg"]
# vws_m_s excluded — ~74% NULL across dataset, imputation not meaningful

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

DDL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=OFF;
CREATE TABLE IF NOT EXISTS dim_station (
    station_id TEXT PRIMARY KEY, station_name TEXT NOT NULL,
    city TEXT NOT NULL, state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dim_pollutant (
    pollutant_id INTEGER PRIMARY KEY AUTOINCREMENT, pollutant_name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS dim_time (
    time_id INTEGER PRIMARY KEY AUTOINCREMENT, dt_str TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL, hour INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS fact_measurements (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT REFERENCES dim_station(station_id),
    pollutant_id INTEGER REFERENCES dim_pollutant(pollutant_id),
    time_id INTEGER REFERENCES dim_time(time_id),
    value REAL, at_c REAL, rh_percent REAL, ws_m_s REAL, wd_deg REAL,
    rf_mm REAL, tot_rf_mm REAL, sr_w_mt2 REAL, bp_mmhg REAL);
"""

def get_files():
    files = sorted([f for f in glob.glob(str(PARQUET_DIR / "**" / "*.parquet"), recursive=True)
                    if not f.endswith(".crc")])
    print(f"Found {len(files)} files")
    if files:
        print("First file:", files[0])
    return files[:MAX_FILES] if MAX_FILES else files

def process(conn, filepath):
    print(repr(filepath)) 
    m = re.search(r"year=(\d+)[/\\]month=(\d+)", filepath)
    yr, mo = int(m.group(1)), int(m.group(2))
    df = pd.read_parquet(filepath)

    # ── Cleaning ──────────────────────────────────────────────────────────────
    df = df[df["value"] >= 0].copy()
    global_medians = df[WEATHER_COLS].median()
    for col in WEATHER_COLS:
        station_med = df.groupby("station_id")[col].transform("median")
        df[col] = df[col].fillna(station_med).fillna(global_medians[col])
    # ─────────────────────────────────────────────────────────────────────────

    df["year"] = yr; df["month"] = mo
    df["dt_str"] = df.apply(lambda r: f"{yr:04d}-{mo:02d}-{int(r.day):02d}T{int(r.hour):02d}:00:00Z", axis=1)

    for _, r in df[["station_id","station_name","city","state"]].drop_duplicates("station_id").iterrows():
        conn.execute("INSERT OR IGNORE INTO dim_station VALUES(?,?,?,?)",
                     (r.station_id, r.station_name, r.city, r.state))
    for p in df["pollutant"].unique():
        conn.execute("INSERT OR IGNORE INTO dim_pollutant(pollutant_name) VALUES(?)", (p,))
    for _, r in df[["dt_str","year","month","day","hour"]].drop_duplicates("dt_str").iterrows():
        conn.execute("INSERT OR IGNORE INTO dim_time(dt_str,year,month,day,hour) VALUES(?,?,?,?,?)",
                     (r.dt_str, yr, mo, int(r.day), int(r.hour)))
    conn.commit()

    poll_map = {r[1]:r[0] for r in conn.execute("SELECT pollutant_id,pollutant_name FROM dim_pollutant")}
    time_map = {r[1]:r[0] for r in conn.execute("SELECT time_id,dt_str FROM dim_time")}

    df["pollutant_id"] = df["pollutant"].map(poll_map)
    df["time_id"]      = df["dt_str"].map(time_map)

    fact_df = df[["station_id","pollutant_id","time_id","value",
                  "at_c","rh_percent","ws_m_s","wd_deg",
                  "rf_mm","tot_rf_mm","sr_w_mt2","bp_mmhg"]]
    fact_df.to_sql("fact_measurements", conn, if_exists="append",
               index=False, chunksize=5000)
    conn.commit()
    return len(fact_df)


def verify(conn):
    log.info("-- Verification ---------------------------------------------")
    for label, q in [("dim_station",      "SELECT COUNT(*) FROM dim_station"),
                     ("dim_pollutant",    "SELECT COUNT(*) FROM dim_pollutant"),
                     ("dim_time",         "SELECT COUNT(*) FROM dim_time"),
                     ("fact_measurements","SELECT COUNT(*) FROM fact_measurements")]:
        log.info(f"  {label:<22}: {conn.execute(q).fetchone()[0]:>10,}")
    log.info("\nAvg PM2.5 by station:")
    for r in conn.execute("""
        SELECT s.station_name, ROUND(AVG(f.value),2)
        FROM   fact_measurements f
        JOIN   dim_station  s ON s.station_id   = f.station_id
        JOIN   dim_pollutant p ON p.pollutant_id = f.pollutant_id
        WHERE  p.pollutant_name = 'pm25'
        GROUP  BY s.station_name
        ORDER  BY 2 DESC""").fetchall():
        log.info(f"  {r[0]:<50} {r[1]}")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    files = get_files()
    log.info(f"Processing {len(files)} partition files -> {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(DDL)
    conn.commit()

    total = 0
    for i, f in enumerate(files, 1):
        n = process(conn, f)
        total += n
        log.info(f"  [{i:>3}/{len(files)}] {Path(f).parent.parent.name}/{Path(f).parent.name}  +{n:,}  (total {total:,})")

    log.info("Building indexes...")
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_fact_station   ON fact_measurements(station_id);
        CREATE INDEX IF NOT EXISTS idx_fact_pollutant ON fact_measurements(pollutant_id);
        CREATE INDEX IF NOT EXISTS idx_fact_time      ON fact_measurements(time_id);
        CREATE INDEX IF NOT EXISTS idx_time_ym        ON dim_time(year, month);
    """)
    conn.commit()

    verify(conn)
    conn.close()
    log.info(f"\nDB: {DB_PATH}  ({DB_PATH.stat().st_size/1e6:.1f} MB)  |  Rows: {total:,}")


if __name__ == "__main__":
    main()