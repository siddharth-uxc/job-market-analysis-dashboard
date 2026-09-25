from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Data Job Market Dashboard",
    page_icon="📊",
    layout="wide",
)


# -----------------------------
# Styling
# -----------------------------

st.markdown(
    """
    <style>
        .stApp {
            background-color: #07111f;
        }

        [data-testid="stSidebar"] {
            background-color: #0b1424;
        }

        .title {
            color: #67e8f9;
            font-size: 42px;
            font-weight: bold;
        }

        .subtitle {
            color: #94a3b8;
            font-size: 18px;
            margin-bottom: 25px;
        }

        .metric-card {
            background-color: #111827;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 14px;
        }

        .metric-value {
            color: #f8fafc;
            font-size: 28px;
            font-weight: bold;
            margin-top: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Load dataset
# -----------------------------

data_file = Path("data/data_jobs_filtered.csv")

if not data_file.exists():
    st.error(
        "The file data/data_jobs_filtered.csv was not found. "
        "Check that your CSV file is inside the data folder."
    )
    st.stop()

df = pd.read_csv(data_file)


# -----------------------------
# Prepare data
# -----------------------------

required_columns = [
    "job_id",
    "title",
    "location",
    "url",
    "updated_at",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"These columns are missing from your CSV file: "
        f"{missing_columns}"
    )
    st.stop()

df["title"] = (
    df["title"]
    .fillna("Unknown title")
    .astype(str)
    .str.strip()
)

df["location"] = (
    df["location"]
    .fillna("Unknown location")
    .astype(str)
    .str.strip()
)

df["url"] = (
    df["url"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["updated_at"] = pd.to_datetime(
    df["updated_at"],
    errors="coerce",
)


# -----------------------------
# Dashboard heading
# -----------------------------

st.markdown(
    '<div class="title">📊 Data Job Market Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Explore data-related job opportunities, job titles, "
    "and hiring locations."
    "</div>",
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar filters
# -----------------------------

st.sidebar.header("Filters")

title_search = st.sidebar.text_input(
    "Search job title",
    placeholder="Example: analyst or engineer",
)

location_list = sorted(
    df["location"].dropna().unique().tolist()
)

selected_locations = st.sidebar.multiselect(
    "Choose location",
    options=location_list,
)

filtered_df = df.copy()

if title_search:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(
            title_search,
            case=False,
            na=False,
        )
    ]

if selected_locations:
    filtered_df = filtered_df[
        filtered_df["location"].isin(selected_locations)
    ]

if filtered_df.empty:
    st.warning("No jobs match your filters.")
    st.stop()


# -----------------------------
# Summary metrics
# -----------------------------

total_jobs = len(filtered_df)
unique_titles = filtered_df["title"].nunique()
unique_locations = filtered_df["location"].nunique()
most_common_title = filtered_df["title"].value_counts().index[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Jobs</div>
            <div class="metric-value">{total_jobs:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Unique Titles</div>
            <div class="metric-value">{unique_titles:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Locations</div>
            <div class="metric-value">{unique_locations:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Most Common Role</div>
            <div class="metric-value">{most_common_title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Job title chart
# -----------------------------

st.subheader("Top Data-Related Job Titles")

title_counts = (
    filtered_df["title"]
    .value_counts()
    .head(15)
    .sort_values()
    .reset_index()
)

title_counts.columns = ["title", "job_count"]

title_chart = px.bar(
    title_counts,
    x="job_count",
    y="title",
    orientation="h",
    color="job_count",
    color_continuous_scale="Tealgrn",
    template="plotly_dark",
)

title_chart.update_layout(
    height=500,
    xaxis_title="Number of jobs",
    yaxis_title="",
    coloraxis_showscale=False,
)

st.plotly_chart(
    title_chart,
    use_container_width=True,
)


# -----------------------------
# Location chart
# -----------------------------

st.subheader("Top Hiring Locations")

location_counts = (
    filtered_df["location"]
    .value_counts()
    .head(15)
    .sort_values()
    .reset_index()
)

location_counts.columns = ["location", "job_count"]

location_chart = px.bar(
    location_counts,
    x="job_count",
    y="location",
    orientation="h",
    color="job_count",
    color_continuous_scale="Purpor",
    template="plotly_dark",
)

location_chart.update_layout(
    height=500,
    xaxis_title="Number of jobs",
    yaxis_title="",
    coloraxis_showscale=False,
)

st.plotly_chart(
    location_chart,
    use_container_width=True,
)


# -----------------------------
# Job listings table
# -----------------------------

st.subheader("Job Listings")

display_columns = [
    "job_id",
    "title",
    "location",
    "updated_at",
    "url",
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
)


# -----------------------------
# Download button
# -----------------------------

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered jobs",
    data=csv_data,
    file_name="filtered_data_jobs.csv",
    mime="text/csv",
)