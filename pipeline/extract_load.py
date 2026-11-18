from pathlib import Path
import dlt
from dlt.sources.rest_api import rest_api_source
import duckdb

DB_PATH = Path("data/jobs.duckdb")
SQL_PATH = Path("pipeline/transform.sql")


def extract_and_load() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    source = rest_api_source({
        "client": {"base_url": "https://remotive.com"},
        "resources": [
            {
                "name": "data_jobs",
                "endpoint": {
                    "path": "remote-jobs",
                    "params": {"category": "data"},
                },
                "write_disposition": "merge",
                "primary_key": "id",
            }
        ],
    })

    pipeline = dlt.pipeline(
        pipeline_name="job_market_pipeline",
        destination=dlt.destinations.duckdb(str(DB_PATH)),
        dataset_name="raw_jobs",
    )

    info = pipeline.run(source)
    print("Load info:", info)


def transform_and_validate() -> None:
    con = duckdb.connect(str(DB_PATH))
    try:
        sql_script = SQL_PATH.read_text(encoding="utf-8")
        con.execute(sql_script)

        # Automated Data Quality Checks
        total_jobs = con.execute("SELECT COUNT(*) FROM analytics.dim_jobs").fetchone()[0]
        null_ids = con.execute(
            "SELECT COUNT(*) FROM analytics.dim_jobs WHERE job_id IS NULL"
        ).fetchone()[0]
        skill_rows = con.execute(
            "SELECT COUNT(*) FROM analytics.fact_skill_demand"
        ).fetchone()[0]

        assert total_jobs > 0, "Data Quality Error: dim_jobs table is empty."
        assert null_ids == 0, f"Data Quality Error: Found {null_ids} null job_ids."
        assert skill_rows > 0, "Data Quality Error: No skills matched in descriptions."

        print(f"Quality checks passed: {total_jobs} jobs, {skill_rows} skill mentions.")
    finally:
        con.close()


if __name__ == "__main__":
    extract_and_load()
    transform_and_validate()
