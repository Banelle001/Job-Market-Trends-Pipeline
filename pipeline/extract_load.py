import dlt
from dlt.sources.rest_api import rest_api_source

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
    destination=dlt.destinations.duckdb("data/jobs.duckdb"),
    dataset_name="raw_jobs",
)

info = pipeline.run(source)
print(info)
