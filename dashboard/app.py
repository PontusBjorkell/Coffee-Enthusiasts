"""Interactive Coffee Enthusiasts analytics dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data" / "dashboard"


st.set_page_config(
    page_title="Coffee Enthusiasts Dashboard",
    page_icon="☕",
    layout="wide",
)


@st.cache_data
def load_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load the analytical datasets exported from SQLite."""

    respondent_profile = pd.read_csv(
        DATA_DIRECTORY / "vw_respondent_profile.csv"
    )

    taste_tests = pd.read_csv(
        DATA_DIRECTORY / "vw_taste_test_analysis.csv"
    )

    coffee_performance = pd.read_csv(
        DATA_DIRECTORY / "vw_coffee_performance.csv"
    )

    expertise_summary = pd.read_csv(
        DATA_DIRECTORY / "vw_expertise_summary.csv"
    )

    return (
        respondent_profile,
        taste_tests,
        coffee_performance,
        expertise_summary,
    )


def calculate_winning_coffee(
    coffee_performance: pd.DataFrame,
) -> str:
    """Return the coffee with the highest average preference."""

    valid_results = coffee_performance.dropna(
        subset=["average_preference"]
    )

    if valid_results.empty:
        return "Not available"

    winner = valid_results.loc[
        valid_results["average_preference"].idxmax(),
        "coffee_code",
    ]

    return f"Coffee {winner}"


def main() -> None:
    """Render the Streamlit dashboard."""

    try:
        (
            respondent_profile,
            taste_tests,
            coffee_performance,
            expertise_summary,
        ) = load_data()
    except FileNotFoundError as error:
        st.error(
            "Dashboard data could not be found. "
            "Run scripts/export_dashboard_data.py first."
        )
        st.exception(error)
        st.stop()

    st.title("☕ Coffee Enthusiasts Dashboard")

    st.markdown(
        """
        Explore consumer profiles, coffee habits, spending patterns,
        and blind taste-test performance from **4,042 survey respondents**.
        """
    )

    st.sidebar.header("Dashboard filters")

    available_age_groups = sorted(
        respondent_profile["age"].dropna().unique()
    )

    selected_age_groups = st.sidebar.multiselect(
        "Age group",
        options=available_age_groups,
        default=available_age_groups,
    )

    available_expertise_segments = [
        segment
        for segment in [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert",
        ]
        if segment
        in respondent_profile["expertise_segment"].dropna().unique()
    ]

    selected_expertise_segments = st.sidebar.multiselect(
        "Expertise segment",
        options=available_expertise_segments,
        default=available_expertise_segments,
    )

    filtered_profiles = respondent_profile[
        respondent_profile["age"].isin(selected_age_groups)
        & respondent_profile["expertise_segment"].isin(
            selected_expertise_segments
        )
    ].copy()

    filtered_ids = filtered_profiles["submission_id"]

    filtered_taste_tests = taste_tests[
        taste_tests["submission_id"].isin(filtered_ids)
    ].copy()

    if filtered_profiles.empty:
        st.warning("No respondents match the selected filters.")
        st.stop()

    total_respondents = filtered_profiles[
        "submission_id"
    ].nunique()

    average_expertise = filtered_profiles["expertise"].mean()

    average_preference = filtered_taste_tests[
        "personal_preference"
    ].mean()

    filtered_coffee_performance = (
        filtered_taste_tests.groupby(
            "coffee_code",
            as_index=False,
        )
        .agg(
            completed_ratings=(
                "personal_preference",
                "count",
            ),
            average_preference=(
                "personal_preference",
                "mean",
            ),
            average_bitterness=(
                "bitterness",
                "mean",
            ),
            average_acidity=(
                "acidity",
                "mean",
            ),
        )
    )

    winning_coffee = calculate_winning_coffee(
        filtered_coffee_performance
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    metric_1.metric(
        label="Respondents",
        value=f"{total_respondents:,}",
    )

    metric_2.metric(
        label="Average expertise",
        value=f"{average_expertise:.2f}",
    )

    metric_3.metric(
        label="Highest-rated coffee",
        value=winning_coffee,
    )

    metric_4.metric(
        label="Average preference",
        value=f"{average_preference:.2f}",
    )

    st.divider()

    chart_1, chart_2 = st.columns(2)

    with chart_1:
        st.subheader("Coffee preference by sample")

        preference_chart = px.bar(
            filtered_coffee_performance,
            x="coffee_code",
            y="average_preference",
            labels={
                "coffee_code": "Coffee sample",
                "average_preference": "Average preference",
            },
            text_auto=".2f",
        )

        preference_chart.update_layout(
            yaxis_range=[0, 5],
            showlegend=False,
        )

        st.plotly_chart(
            preference_chart,
            use_container_width=True,
        )

    with chart_2:
        st.subheader("Respondents by expertise segment")

        filtered_expertise = (
            filtered_profiles.groupby(
                "expertise_segment",
                as_index=False,
            )
            .agg(
                respondents=("submission_id", "nunique")
            )
        )

        expertise_chart = px.pie(
            filtered_expertise,
            names="expertise_segment",
            values="respondents",
            hole=0.55,
        )

        st.plotly_chart(
            expertise_chart,
            use_container_width=True,
        )

    chart_3, chart_4 = st.columns(2)

    with chart_3:
        st.subheader("Monthly coffee spending")

        spending_order = [
            "<$20",
            "$20-$40",
            "$40-$60",
            "$60-$80",
            "$80-$100",
            ">$100",
        ]

        spending_distribution = (
            filtered_profiles[
                "monthly_coffee_spend"
            ]
            .value_counts()
            .reindex(spending_order)
            .dropna()
            .reset_index()
        )

        spending_distribution.columns = [
            "monthly_coffee_spend",
            "respondents",
        ]

        spending_chart = px.bar(
            spending_distribution,
            x="monthly_coffee_spend",
            y="respondents",
            labels={
                "monthly_coffee_spend": "Monthly spend",
                "respondents": "Respondents",
            },
        )

        st.plotly_chart(
            spending_chart,
            use_container_width=True,
        )

    with chart_4:
        st.subheader("Preferred roast level")

        roast_distribution = (
            filtered_profiles[
                "preferred_roast_level"
            ]
            .value_counts()
            .reset_index()
        )

        roast_distribution.columns = [
            "preferred_roast_level",
            "respondents",
        ]

        roast_chart = px.bar(
            roast_distribution,
            x="respondents",
            y="preferred_roast_level",
            orientation="h",
            labels={
                "preferred_roast_level": "Roast level",
                "respondents": "Respondents",
            },
        )

        roast_chart.update_layout(
            yaxis={
                "categoryorder": "total ascending",
            }
        )

        st.plotly_chart(
            roast_chart,
            use_container_width=True,
        )

    st.divider()

    st.subheader("Sensory profile by coffee sample")

    sensory_data = filtered_coffee_performance.melt(
        id_vars=["coffee_code"],
        value_vars=[
            "average_bitterness",
            "average_acidity",
        ],
        var_name="sensory_measure",
        value_name="average_rating",
    )

    sensory_data["sensory_measure"] = sensory_data[
        "sensory_measure"
    ].replace(
        {
            "average_bitterness": "Bitterness",
            "average_acidity": "Acidity",
        }
    )

    sensory_chart = px.bar(
        sensory_data,
        x="coffee_code",
        y="average_rating",
        color="sensory_measure",
        barmode="group",
        labels={
            "coffee_code": "Coffee sample",
            "average_rating": "Average sensory rating",
            "sensory_measure": "Measure",
        },
    )

    sensory_chart.update_layout(
        yaxis_range=[0, 5],
    )

    st.plotly_chart(
        sensory_chart,
        use_container_width=True,
    )

    with st.expander("View filtered coffee performance data"):
        st.dataframe(
            filtered_coffee_performance.round(2),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()