import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Data Job Market Pulse", layout="wide")


@st.cache_data(ttl=3600)
def load_data():
    con = duckdb.connect("data/jobs.duckdb", read_only=True)
    jobs = con.execute("SELECT * FROM analytics.dim_jobs").df()
    skills = con.execute("SELECT * FROM analytics.fact_skill_demand").df()
    con.close()
    return jobs, skills


jobs_df, skills_df = load_data()

st.title("Data Analytics Job Market Pulse")
st.caption("Automated daily ELT pipeline powered by Python, dlt, DuckDB, and GitHub Actions.")

# Sidebar filters
st.sidebar.header("Filters")
seniority_options = sorted(jobs_df["seniority_level"].unique().tolist())
selected_seniority = st.sidebar.multiselect(
    "Seniority Level", seniority_options, default=seniority_options
)

filtered_jobs = jobs_df[jobs_df["seniority_level"].isin(selected_seniority)]
filtered_skills = skills_df[skills_df["seniority_level"].isin(selected_seniority)]

# KPI Row
col1, col2, col3, col4 = st.columns(4)
total_count = len(filtered_jobs)
entry_count = len(filtered_jobs[filtered_jobs["seniority_level"] == "Entry / Junior"])
top_skill = (
    filtered_skills["skill"].value_counts().index[0]
    if not filtered_skills.empty
    else "N/A"
)
latest_date = pd.to_datetime(filtered_jobs["published_date"]).max()

col1.metric("Total Active Postings", f"{total_count:,}")
col2.metric("Entry / Junior Roles", f"{entry_count:,}")
col3.metric("Most Requested Skill", top_skill)
col4.metric("Latest Posting Date", latest_date.strftime("%Y-%m-%d") if pd.notna(latest_date) else "N/A")

st.divider()

# Charts Row
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Top In-Demand Technical Skills")
    skill_counts = (
        filtered_skills.groupby("skill")["job_id"]
        .nunique()
        .reset_index(name="job_count")
        .sort_values("job_count", ascending=True)
    )
    skill_counts["pct_of_jobs"] = (skill_counts["job_count"] / max(total_count, 1) * 100).round(1)

    fig_skills = px.bar(
        skill_counts,
        x="pct_of_jobs",
        y="skill",
        orientation="h",
        text="pct_of_jobs",
        labels={"pct_of_jobs": "% of Job Postings", "skill": ""},
    )
    fig_skills.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_skills.update_layout(height=420, margin=dict(l=10, r=30, t=10, b=10))
    st.plotly_chart(fig_skills, use_container_width=True)

with right_col:
    st.subheader("Job Postings Over Time")
    trend_df = (
        filtered_jobs.groupby(["published_date", "seniority_level"])["job_id"]
        .count()
        .reset_index(name="postings")
        .sort_values("published_date")
    )
    fig_trend = px.area(
        trend_df,
        x="published_date",
        y="postings",
        color="seniority_level",
        labels={"published_date": "Date", "postings": "Postings", "seniority_level": "Level"},
    )
    fig_trend.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)

# Recent Postings Table
st.subheader("Latest Job Postings")
display_cols = ["published_date", "job_title", "company_name", "seniority_level", "location", "job_url"]
st.dataframe(
    filtered_jobs.sort_values("published_at", ascending=False)[display_cols].head(25),
    use_container_width=True,
    hide_index=True,
    column_config={"job_url": st.column_config.LinkColumn("Apply Link")},
)

