# Job-Market-Trends-Pipeline

job-market-pulse/
├── .github/workflows/
│   └── daily_pipeline.yml      # Runs pipeline daily & commits updated DB
├── pipeline/
│   ├── extract_load.py         # Pulls API data via dlt into DuckDB
│   └── transform.sql           # Cleans titles, extracts skills, builds KPIs
├── app/
│   └── dashboard.py            # Live Streamlit dashboard
├── data/
│   └── jobs.duckdb             # Lightweight analytical database file
├── requirements.txt
└── README.md                   # Architecture diagram, live link & key insights
