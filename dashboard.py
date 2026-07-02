import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------------------------------
# Page setup
# -----------------------------------------------------

st.set_page_config(
    page_title="Energy Regulatory Friction Dashboard",
    layout="wide"
)

# -----------------------------------------------------
# CCC brand styling
# -----------------------------------------------------

CCC_BLUE = "#293993"
CCC_ORANGE = "#EE8A1D"
CCC_DARK_GREY = "#494949"
CCC_LIGHT_GREY = "#F1F2F7"
CCC_MID_GREY = "#969696"
CCC_WHITE = "#FFFFFF"

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: Arial, sans-serif;
        color: {CCC_DARK_GREY};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }}

    .ccc-hero {{
        background: {CCC_BLUE};
        padding: 34px 38px;
        border-radius: 18px;
        margin-bottom: 28px;
        border-left: 12px solid {CCC_ORANGE};
    }}

    .ccc-kicker {{
        color: {CCC_ORANGE};
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}

    .ccc-title {{
        color: {CCC_WHITE};
        font-size: 2.45rem;
        font-weight: 900;
        line-height: 1.05;
        text-transform: uppercase;
        letter-spacing: -0.02em;
        margin-bottom: 12px;
    }}

    .ccc-subtitle {{
        color: {CCC_WHITE};
        opacity: 0.94;
        font-size: 1.02rem;
        line-height: 1.45;
        max-width: 920px;
    }}

    h1, h2, h3 {{
        color: {CCC_BLUE};
        font-weight: 900 !important;
        letter-spacing: -0.02em;
    }}

    h2, h3 {{
        text-transform: uppercase;
    }}

    .section-note {{
        color: {CCC_DARK_GREY};
        background: {CCC_LIGHT_GREY};
        border-left: 6px solid {CCC_ORANGE};
        padding: 14px 18px;
        border-radius: 12px;
        font-size: 0.94rem;
        line-height: 1.45;
        margin-top: 8px;
        margin-bottom: 22px;
    }}

    div[data-testid="stMetric"] {{
        background: {CCC_WHITE};
        border: 1px solid #E2E4EF;
        border-top: 6px solid {CCC_ORANGE};
        padding: 18px 18px 16px 18px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(41, 57, 147, 0.06);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {CCC_BLUE};
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    div[data-testid="stMetricValue"] {{
        color: {CCC_DARK_GREY};
        font-size: 1.8rem;
        font-weight: 900;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {CCC_LIGHT_GREY};
        color: {CCC_BLUE};
        border-radius: 999px;
        padding: 8px 18px;
        font-weight: 800;
    }}

    .stTabs [aria-selected="true"] {{
        background: {CCC_BLUE} !important;
        color: white !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #F7F7FB;
        border-right: 1px solid #E2E4EF;
    }}

    .small-muted {{
        color: {CCC_MID_GREY};
        font-size: 0.9rem;
    }}

    .callout-card {{
        background: {CCC_LIGHT_GREY};
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #E2E4EF;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------
# Load data
# -----------------------------------------------------

data_path = Path("outputs/tables/project_friction_index.csv")

if not data_path.exists():
    st.error(f"Could not find the dataset at: {data_path}")
    st.info("Check that `project_friction_index.csv` exists in `outputs/tables/`.")
    st.stop()

df = pd.read_csv(data_path)
df.columns = df.columns.str.strip()

numeric_columns = [
    "capex_billion",
    "friction_weighted_capex_billion",
    "adjusted_friction_index_0_100",
    "raw_friction_index_0_100",
    "evidence_score",
    "delay_years_by_2026",
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# -----------------------------------------------------
# Helper functions
# -----------------------------------------------------

def money_billion(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"${value:,.1f}B"


def percent(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def get_score_column(data):
    if "adjusted_friction_index_0_100" in data.columns:
        return "adjusted_friction_index_0_100"
    if "raw_friction_index_0_100" in data.columns:
        return "raw_friction_index_0_100"
    return None


def apply_ccc_chart_style(fig, height=None):
    fig.update_layout(
        font=dict(family="Arial", color=CCC_DARK_GREY),
        paper_bgcolor=CCC_WHITE,
        plot_bgcolor=CCC_WHITE,
        margin=dict(l=10, r=10, t=30, b=20),
        height=height,
        xaxis=dict(
            showgrid=True,
            gridcolor="#ECEEF6",
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        )
    )
    return fig


# -----------------------------------------------------
# Header
# -----------------------------------------------------

st.markdown(
    """
    <div class="ccc-hero">
        <div class="ccc-kicker">Consumer Choice Center | Policy Research Dashboard</div>
        <div class="ccc-title">Energy Regulatory Friction Dashboard</div>
        <div class="ccc-subtitle">
            A project-level view of proposed Canadian energy, mining, LNG, pipeline,
            offshore oil, and related infrastructure investment exposure to regulatory friction.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------
# Sidebar filters
# -----------------------------------------------------

st.sidebar.markdown("### FILTERS")
st.sidebar.caption("Explore the project dataset by geography, status, cause, and project type.")

filtered_df = df.copy()

if "province_state" in filtered_df.columns:
    provinces = sorted(filtered_df["province_state"].dropna().unique())
    selected_provinces = st.sidebar.multiselect(
        "Province / State",
        provinces,
        default=provinces
    )
    filtered_df = filtered_df[filtered_df["province_state"].isin(selected_provinces)]

if "status_3cat" in filtered_df.columns:
    statuses = sorted(filtered_df["status_3cat"].dropna().unique())
    selected_statuses = st.sidebar.multiselect(
        "Project status",
        statuses,
        default=statuses
    )
    filtered_df = filtered_df[filtered_df["status_3cat"].isin(selected_statuses)]

if "regulatory_bucket" in filtered_df.columns:
    buckets = sorted(filtered_df["regulatory_bucket"].dropna().unique())
    selected_buckets = st.sidebar.multiselect(
        "Cause bucket",
        buckets,
        default=buckets
    )
    filtered_df = filtered_df[filtered_df["regulatory_bucket"].isin(selected_buckets)]

if "project_type" in filtered_df.columns:
    project_types = sorted(filtered_df["project_type"].dropna().unique())
    selected_project_types = st.sidebar.multiselect(
        "Project type",
        project_types,
        default=project_types
    )
    filtered_df = filtered_df[filtered_df["project_type"].isin(selected_project_types)]

st.sidebar.divider()

if st.sidebar.button("Reset filters"):
    st.rerun()

# -----------------------------------------------------
# Metrics
# -----------------------------------------------------

total_projects = len(filtered_df)

total_capex = (
    filtered_df["capex_billion"].sum()
    if "capex_billion" in filtered_df.columns
    else None
)

weighted_capex = (
    filtered_df["friction_weighted_capex_billion"].sum()
    if "friction_weighted_capex_billion" in filtered_df.columns
    else None
)

weighted_share = (
    weighted_capex / total_capex * 100
    if total_capex and weighted_capex is not None and total_capex != 0
    else None
)

score_col = get_score_column(filtered_df)

avg_score = (
    filtered_df[score_col].mean()
    if score_col
    else None
)

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("Projects analyzed", f"{total_projects}")

with metric2:
    st.metric("Total proposed exposure", money_billion(total_capex))

with metric3:
    st.metric("Friction-weighted exposure", money_billion(weighted_capex))

with metric4:
    st.metric("Weighted exposure share", percent(weighted_share))

st.markdown(
    """
    <div class="section-note">
    Friction-weighted exposure is not a claim that every dollar was lost because of regulation.
    It weights proposed investment by project outcome, cause classification, and evidence quality.
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------
# Tabs
# -----------------------------------------------------

tab_overview, tab_projects, tab_breakdowns, tab_methodology = st.tabs(
    ["Overview", "Project Explorer", "Breakdowns", "Methodology Notes"]
)

# -----------------------------------------------------
# Overview
# -----------------------------------------------------

with tab_overview:
    st.subheader("Overview")

    left, right = st.columns([1.1, 0.9])

    with left:
        st.markdown(
            """
            This dashboard summarizes a project-level analysis of proposed capital expenditure
            exposure across major Canadian energy and resource projects.

            The key measure is **friction-weighted exposure**, which adjusts project capex by
            project outcome, cause classification, and evidence quality. The goal is to separate
            projects mainly affected by market conditions from projects where regulatory delay,
            legal uncertainty, consultation risk, policy uncertainty, or government decisions
            were material factors.
            """
        )

    with right:
        snapshot_rows = []

        if "regulatory_bucket" in filtered_df.columns and not filtered_df["regulatory_bucket"].dropna().empty:
            snapshot_rows.append({
                "Measure": "Most common cause bucket",
                "Value": filtered_df["regulatory_bucket"].dropna().value_counts().idxmax()
            })

        if "project_type" in filtered_df.columns and not filtered_df["project_type"].dropna().empty:
            snapshot_rows.append({
                "Measure": "Most common project type",
                "Value": filtered_df["project_type"].dropna().value_counts().idxmax()
            })

        if avg_score is not None:
            snapshot_rows.append({
                "Measure": "Average friction score",
                "Value": f"{avg_score:.1f}/100"
            })

        snapshot_rows.append({
            "Measure": "Current filtered projects",
            "Value": str(total_projects)
        })

        st.markdown('<div class="callout-card">', unsafe_allow_html=True)
        st.markdown("#### Dataset Snapshot")
        st.dataframe(
            pd.DataFrame(snapshot_rows),
            use_container_width=True,
            hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("#### Friction-weighted exposure by cause bucket")

        if {"regulatory_bucket", "friction_weighted_capex_billion"}.issubset(filtered_df.columns):
            bucket_chart = (
                filtered_df
                .groupby("regulatory_bucket", as_index=False)["friction_weighted_capex_billion"]
                .sum()
                .sort_values("friction_weighted_capex_billion", ascending=False)
            )

            fig = px.bar(
                bucket_chart,
                x="regulatory_bucket",
                y="friction_weighted_capex_billion",
                text_auto=".1f",
                color_discrete_sequence=[CCC_BLUE]
            )
            fig.update_traces(
                marker_line_color=CCC_ORANGE,
                marker_line_width=1.5,
                textposition="outside"
            )
            fig.update_layout(
                xaxis_title=None,
                yaxis_title="Friction-weighted exposure, $B"
            )
            st.plotly_chart(apply_ccc_chart_style(fig, height=430), use_container_width=True)
        else:
            st.warning("Missing columns needed for this chart.")

    with chart_right:
        st.markdown("#### Largest projects by proposed capex")

        if {"project", "capex_billion"}.issubset(filtered_df.columns):
            top_capex = (
                filtered_df
                .sort_values("capex_billion", ascending=False)
                .head(10)
            )

            fig = px.bar(
                top_capex,
                x="capex_billion",
                y="project",
                orientation="h",
                text_auto=".1f",
                color_discrete_sequence=[CCC_ORANGE]
            )
            fig.update_traces(marker_line_color=CCC_BLUE, marker_line_width=1.2)
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_title="Proposed capex, $B",
                yaxis_title=None
            )
            st.plotly_chart(apply_ccc_chart_style(fig, height=430), use_container_width=True)
        else:
            st.warning("Missing columns needed for this chart.")

# -----------------------------------------------------
# Project Explorer
# -----------------------------------------------------

with tab_projects:
    st.subheader("Project Explorer")
    st.caption("Search, filter, and download the project-level dataset.")

    search_term = st.text_input("Search project names", "")

    project_table = filtered_df.copy()

    if search_term and "project" in project_table.columns:
        project_table = project_table[
            project_table["project"]
            .astype(str)
            .str.contains(search_term, case=False, na=False)
        ]

    preferred_columns = [
        "project",
        "province_state",
        "project_type",
        "capex_billion",
        "status_3cat",
        "regulatory_bucket",
        "adjusted_friction_index_0_100",
        "friction_weighted_capex_billion",
        "evidence_score",
        "source_type",
        "source_link",
    ]

    visible_columns = [col for col in preferred_columns if col in project_table.columns]
    display_table = project_table[visible_columns].copy() if visible_columns else project_table.copy()

    column_config = {}

    if "capex_billion" in display_table.columns:
        column_config["capex_billion"] = st.column_config.NumberColumn(
            "Proposed capex, $B",
            format="$%.1fB"
        )

    if "friction_weighted_capex_billion" in display_table.columns:
        column_config["friction_weighted_capex_billion"] = st.column_config.NumberColumn(
            "Friction-weighted exposure, $B",
            format="$%.1fB"
        )

    if "adjusted_friction_index_0_100" in display_table.columns:
        column_config["adjusted_friction_index_0_100"] = st.column_config.NumberColumn(
            "Friction score",
            format="%.1f"
        )

    if "source_link" in display_table.columns:
        column_config["source_link"] = st.column_config.LinkColumn("Source link")

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        column_config=column_config
    )

    csv = project_table.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered project data",
        data=csv,
        file_name="filtered_energy_friction_projects.csv",
        mime="text/csv"
    )

# -----------------------------------------------------
# Breakdowns
# -----------------------------------------------------

with tab_breakdowns:
    st.subheader("Breakdowns")

    row1_left, row1_right = st.columns(2)

    with row1_left:
        st.markdown("#### Proposed capex by project status")

        if {"status_3cat", "capex_billion"}.issubset(filtered_df.columns):
            status_chart = (
                filtered_df
                .groupby("status_3cat", as_index=False)["capex_billion"]
                .sum()
                .sort_values("capex_billion", ascending=False)
            )

            fig = px.bar(
                status_chart,
                x="status_3cat",
                y="capex_billion",
                text_auto=".1f",
                color_discrete_sequence=[CCC_BLUE]
            )
            fig.update_traces(marker_line_color=CCC_ORANGE, marker_line_width=1.5)
            fig.update_layout(
                xaxis_title=None,
                yaxis_title="Proposed capex, $B"
            )
            st.plotly_chart(apply_ccc_chart_style(fig, height=420), use_container_width=True)
        else:
            st.warning("Missing columns needed for this chart.")

    with row1_right:
        st.markdown("#### Proposed capex by project type")

        if {"project_type", "capex_billion"}.issubset(filtered_df.columns):
            type_chart = (
                filtered_df
                .groupby("project_type", as_index=False)["capex_billion"]
                .sum()
                .sort_values("capex_billion", ascending=False)
            )

            fig = px.bar(
                type_chart,
                x="project_type",
                y="capex_billion",
                text_auto=".1f",
                color_discrete_sequence=[CCC_ORANGE]
            )
            fig.update_traces(marker_line_color=CCC_BLUE, marker_line_width=1.2)
            fig.update_layout(
                xaxis_title=None,
                yaxis_title="Proposed capex, $B"
            )
            st.plotly_chart(apply_ccc_chart_style(fig, height=420), use_container_width=True)
        else:
            st.warning("Missing columns needed for this chart.")

    st.divider()

    row2_left, row2_right = st.columns(2)

    with row2_left:
        st.markdown("#### Project friction scores")

        if score_col and {"project", score_col}.issubset(filtered_df.columns):
            score_chart = (
                filtered_df
                .sort_values(score_col, ascending=False)
                .head(15)
            )

            fig = px.bar(
                score_chart,
                x=score_col,
                y="project",
                orientation="h",
                text_auto=".1f",
                color_discrete_sequence=[CCC_BLUE]
            )
            fig.update_traces(marker_line_color=CCC_ORANGE, marker_line_width=1.5)
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_title="Friction score",
                yaxis_title=None
            )
            st.plotly_chart(apply_ccc_chart_style(fig, height=500), use_container_width=True)
        else:
            st.warning("Missing columns needed for this chart.")

    with row2_right:
        st.markdown("#### Friction-weighted exposure by project")

        if {"project", "friction_weighted_capex_billion"}.issubset(filtered_df.columns):
            exposure_chart = (
                filtered_df
                .sort_values("friction_weighted_capex_billion", ascending=False)
                .head(15)
            )

            fig = px.bar(
                exposure_chart,
                x="friction_weighted_capex_billion",
                y="project",
                orientation="h",
                text_auto=".1f",
                color_discrete_sequence=[CCC_ORANGE]
            )
            fig.update_traces(marker_line_color=CCC_BLUE, marker_line_width=1.2)
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_title="Friction-weighted exposure, $B",
                yaxis_title=None
            )
            st.plotly_chart(apply_ccc_chart_style(fig, height=500), use_container_width=True)
        else:
            st.warning("Missing columns needed for this chart.")

# -----------------------------------------------------
# Methodology
# -----------------------------------------------------

with tab_methodology:
    st.subheader("Methodology Notes")

    st.markdown(
        """
        This dashboard is intended as a project-level screening and summary tool.

        **Total proposed investment exposure** is the sum of proposed capital expenditure
        for the projects included in the dataset.

        **Friction-weighted exposure** adjusts proposed capex using the project’s outcome,
        cause classification, and evidence quality. This is designed to separate projects
        mainly affected by market conditions from projects where regulatory delay, legal
        uncertainty, consultation risk, policy uncertainty, or government decisions were
        material factors.

        **Weighted exposure share** is calculated as:

        `friction-weighted exposure / total proposed investment exposure`

        This should not be interpreted as a direct GDP loss or as a claim that all affected
        investment was lost exclusively because of regulation.
        """
    )

    st.markdown(
        """
        <div class="section-note">
        Best use: combine this dashboard with the written policy note and source table,
        especially when explaining individual project classifications.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("Columns available in the loaded dataset"):
        st.write(list(df.columns))

    with st.expander("Current data source"):
        st.code(str(data_path))