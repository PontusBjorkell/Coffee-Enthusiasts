"""Interactive Coffee Enthusiasts analytics dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "dashboard"
)

EXPERTISE_ORDER = [
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
]

SPENDING_ORDER = [
    "<$20",
    "$20-$40",
    "$40-$60",
    "$60-$80",
    "$80-$100",
    ">$100",
]

COFFEE_ORDER = [
    "A",
    "B",
    "C",
    "D",
]


st.set_page_config(
    page_title="Coffee Enthusiasts Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    """Load analytical datasets exported from SQLite."""

    filenames = {
        "respondent_profile": (
            "vw_respondent_profile.csv"
        ),
        "taste_tests": (
            "vw_taste_test_analysis.csv"
        ),
        "coffee_performance": (
            "vw_coffee_performance.csv"
        ),
        "expertise_summary": (
            "vw_expertise_summary.csv"
        ),
        "segment_performance": (
            "vw_segment_coffee_performance.csv"
        ),
    }

    datasets: dict[str, pd.DataFrame] = {}

    for dataset_name, filename in filenames.items():
        path = DATA_DIRECTORY / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required dashboard file not found: {path}"
            )

        datasets[dataset_name] = pd.read_csv(path)

    return datasets


def ordered_available_values(
    values: pd.Series,
    preferred_order: list[str],
) -> list[str]:
    """Return present values in a preferred business order."""

    present_values = {
        str(value)
        for value in values.dropna().unique()
    }

    ordered_values = [
        value
        for value in preferred_order
        if value in present_values
    ]

    remaining_values = sorted(
        present_values.difference(
            ordered_values
        )
    )

    return ordered_values + remaining_values


def format_coffee_label(
    coffee_code: object,
) -> str:
    """Format a coffee code for display."""

    if pd.isna(coffee_code):
        return "Not available"

    value = str(coffee_code).strip()

    if value.lower().startswith("coffee"):
        return value

    return f"Coffee {value}"


def calculate_coffee_performance(
    taste_tests: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate coffee metrics for the current filters."""

    performance = (
        taste_tests.groupby(
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
            preference_standard_deviation=(
                "personal_preference",
                "std",
            ),
        )
    )

    performance["coffee_code"] = pd.Categorical(
        performance["coffee_code"],
        categories=COFFEE_ORDER,
        ordered=True,
    )

    performance = performance.sort_values(
        "coffee_code"
    )

    performance["coffee_label"] = (
        performance["coffee_code"]
        .astype("string")
        .map(format_coffee_label)
    )

    return performance


def get_winner(
    performance: pd.DataFrame,
) -> tuple[str, float | None]:
    """Return the winning coffee and its average rating."""

    valid_results = performance.dropna(
        subset=["average_preference"]
    )

    if valid_results.empty:
        return "Not available", None

    winner_row = valid_results.loc[
        valid_results[
            "average_preference"
        ].idxmax()
    ]

    return (
        format_coffee_label(
            winner_row["coffee_code"]
        ),
        float(
            winner_row["average_preference"]
        ),
    )


def calculate_segment_performance(
    taste_tests: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate average preference by expertise and coffee."""

    segment_performance = (
        taste_tests.dropna(
            subset=[
                "expertise_segment",
                "personal_preference",
            ]
        )
        .groupby(
            [
                "expertise_segment",
                "coffee_code",
            ],
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
        )
    )

    segment_performance[
        "expertise_segment"
    ] = pd.Categorical(
        segment_performance[
            "expertise_segment"
        ],
        categories=EXPERTISE_ORDER,
        ordered=True,
    )

    segment_performance[
        "coffee_code"
    ] = pd.Categorical(
        segment_performance[
            "coffee_code"
        ],
        categories=COFFEE_ORDER,
        ordered=True,
    )

    segment_performance["coffee_label"] = (
        segment_performance["coffee_code"]
        .astype("string")
        .map(format_coffee_label)
    )

    return segment_performance.sort_values(
        [
            "expertise_segment",
            "coffee_code",
        ]
    )


def create_preference_insight(
    performance: pd.DataFrame,
) -> str:
    """Create a concise interpretation of coffee performance."""

    ranked = (
        performance.dropna(
            subset=["average_preference"]
        )
        .sort_values(
            "average_preference",
            ascending=False,
        )
    )

    if ranked.empty:
        return (
            "No preference ratings are available "
            "for the selected filters."
        )

    winner = ranked.iloc[0]

    if len(ranked) == 1:
        return (
            f"{winner['coffee_label']} has an "
            f"average preference rating of "
            f"{winner['average_preference']:.2f}."
        )

    runner_up = ranked.iloc[1]

    difference = (
        winner["average_preference"]
        - runner_up["average_preference"]
    )

    return (
        f"{winner['coffee_label']} is the "
        f"highest-rated sample for the current "
        f"selection at "
        f"{winner['average_preference']:.2f}/5. "
        f"It leads {runner_up['coffee_label']} "
        f"by {difference:.2f} rating points."
    )


def create_spending_insight(
    profiles: pd.DataFrame,
) -> str:
    """Create a spending interpretation for selected respondents."""

    spending = profiles[
        "estimated_monthly_spend"
    ].dropna()

    if spending.empty:
        return (
            "No spending estimates are available "
            "for the selected respondents."
        )

    premium_rate = (
        profiles["is_premium_customer"]
        .fillna(0)
        .mean()
        * 100
    )

    return (
        "Estimated average monthly spending is "
        f"${spending.mean():.0f}. "
        f"Approximately {premium_rate:.1f}% meet "
        "the project's premium-customer definition."
    )


def render_sidebar(
    respondent_profile: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Render dashboard filters and return selected values."""

    st.sidebar.header("Dashboard filters")

    age_groups = sorted(
        respondent_profile["age"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    expertise_segments = ordered_available_values(
        respondent_profile[
            "expertise_segment"
        ],
        EXPERTISE_ORDER,
    )

    selected_age_groups = st.sidebar.multiselect(
        "Age group",
        options=age_groups,
        default=age_groups,
        help=(
            "Filter every dashboard section "
            "by survey age category."
        ),
    )

    selected_expertise_segments = (
        st.sidebar.multiselect(
            "Expertise segment",
            options=expertise_segments,
            default=expertise_segments,
            help=(
                "Beginner: 1-3, Intermediate: 4-6, "
                "Advanced: 7-8, Expert: 9-10."
            ),
        )
    )

    st.sidebar.divider()

    st.sidebar.caption(
        "Preference, acidity, and bitterness use "
        "1-5 survey rating scales."
    )

    st.sidebar.caption(
        "Expertise is self-reported on a 1-10 scale."
    )

    return (
        selected_age_groups,
        selected_expertise_segments,
    )


def render_overview_tab(
    filtered_profiles: pd.DataFrame,
    filtered_taste_tests: pd.DataFrame,
    filtered_performance: pd.DataFrame,
    overall_performance: pd.DataFrame,
) -> None:
    """Render the executive overview."""

    total_respondents = filtered_profiles[
        "submission_id"
    ].nunique()

    average_expertise = filtered_profiles[
        "expertise"
    ].mean()

    average_preference = filtered_taste_tests[
        "personal_preference"
    ].mean()

    estimated_spend = filtered_profiles[
        "estimated_monthly_spend"
    ].mean()

    filtered_winner, winner_rating = get_winner(
        filtered_performance
    )

    overall_winner, _ = get_winner(
        overall_performance
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    metric_1.metric(
        label="Respondents",
        value=f"{total_respondents:,}",
    )

    metric_2.metric(
        label="Average expertise",
        value=(
            f"{average_expertise:.2f}/10"
            if pd.notna(average_expertise)
            else "Not available"
        ),
    )

    metric_3.metric(
        label="Highest-rated coffee",
        value=filtered_winner,
        delta=(
            f"Overall winner: {overall_winner}"
            if filtered_winner != overall_winner
            else "Matches overall winner"
        ),
        delta_color="off",
    )

    metric_4.metric(
        label="Estimated monthly spend",
        value=(
            f"${estimated_spend:.0f}"
            if pd.notna(estimated_spend)
            else "Not available"
        ),
        help=(
            "Estimated from categorical spending "
            "bands; this is not exact respondent spending."
        ),
    )

    if pd.notna(average_preference):
        st.caption(
            "Average preference across all completed "
            f"ratings: {average_preference:.2f}/5"
        )

    chart_1, chart_2 = st.columns(
        [1.4, 1]
    )

    with chart_1:
        st.subheader(
            "Average preference by coffee"
        )

        preference_chart = px.bar(
            filtered_performance,
            x="coffee_label",
            y="average_preference",
            text_auto=".2f",
            custom_data=[
                "completed_ratings",
                "preference_standard_deviation",
            ],
            labels={
                "coffee_label": "Coffee sample",
                (
                    "average_preference"
                ): "Average preference",
            },
        )

        preference_chart.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average preference: %{y:.2f}<br>"
                "Completed ratings: "
                "%{customdata[0]:,.0f}<br>"
                "Rating standard deviation: "
                "%{customdata[1]:.2f}"
                "<extra></extra>"
            )
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
        st.subheader(
            "Respondents by expertise"
        )

        expertise_distribution = (
            filtered_profiles.groupby(
                "expertise_segment",
                as_index=False,
            )
            .agg(
                respondents=(
                    "submission_id",
                    "nunique",
                )
            )
        )

        expertise_distribution[
            "expertise_segment"
        ] = pd.Categorical(
            expertise_distribution[
                "expertise_segment"
            ],
            categories=EXPERTISE_ORDER,
            ordered=True,
        )

        expertise_distribution = (
            expertise_distribution.sort_values(
                "expertise_segment"
            )
        )

        expertise_chart = px.pie(
            expertise_distribution,
            names="expertise_segment",
            values="respondents",
            hole=0.55,
        )

        expertise_chart.update_traces(
            textposition="inside",
            textinfo="percent+label",
        )

        st.plotly_chart(
            expertise_chart,
            use_container_width=True,
        )

    st.info(
        create_preference_insight(
            filtered_performance
        )
    )

    if winner_rating is not None:
        st.caption(
            "Rankings are descriptive and do not by "
            "themselves establish statistical significance."
        )


def render_taste_tab(
    filtered_profiles: pd.DataFrame,
    filtered_taste_tests: pd.DataFrame,
    filtered_performance: pd.DataFrame,
) -> None:
    """Render taste-test and expertise analysis."""

    st.subheader(
        "Do expertise segments rate coffees differently?"
    )

    segment_performance = (
        calculate_segment_performance(
            filtered_taste_tests
        )
    )

    segment_chart = px.line(
        segment_performance,
        x="expertise_segment",
        y="average_preference",
        color="coffee_label",
        markers=True,
        custom_data=["completed_ratings"],
        category_orders={
            "expertise_segment": EXPERTISE_ORDER,
            "coffee_label": [
                "Coffee A",
                "Coffee B",
                "Coffee C",
                "Coffee D",
            ],
        },
        labels={
            (
                "expertise_segment"
            ): "Expertise segment",
            (
                "average_preference"
            ): "Average preference",
            "coffee_label": "Coffee",
        },
    )

    segment_chart.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Segment: %{x}<br>"
            "Average preference: %{y:.2f}<br>"
            "Completed ratings: "
            "%{customdata[0]:,.0f}"
            "<extra></extra>"
        )
    )

    segment_chart.update_layout(
        yaxis_range=[0, 5],
    )

    st.plotly_chart(
        segment_chart,
        use_container_width=True,
    )

    st.caption(
        "Differences shown here are descriptive. "
        "Refer to the notebook's statistical tests "
        "before describing a difference as significant."
    )

    sensory_data = filtered_performance.melt(
        id_vars=[
            "coffee_code",
            "coffee_label",
        ],
        value_vars=[
            "average_bitterness",
            "average_acidity",
        ],
        var_name="sensory_measure",
        value_name="average_rating",
    )

    sensory_data["sensory_measure"] = (
        sensory_data["sensory_measure"]
        .replace(
            {
                (
                    "average_bitterness"
                ): "Bitterness",
                (
                    "average_acidity"
                ): "Acidity",
            }
        )
    )

    chart_1, chart_2 = st.columns(2)

    with chart_1:
        st.subheader(
            "Sensory profile by coffee"
        )

        sensory_chart = px.bar(
            sensory_data,
            x="coffee_label",
            y="average_rating",
            color="sensory_measure",
            barmode="group",
            text_auto=".2f",
            labels={
                "coffee_label": "Coffee sample",
                (
                    "average_rating"
                ): "Average sensory rating",
                (
                    "sensory_measure"
                ): "Measure",
            },
        )

        sensory_chart.update_layout(
            yaxis_range=[0, 5],
        )

        st.plotly_chart(
            sensory_chart,
            use_container_width=True,
        )

    with chart_2:
        st.subheader(
            "Final overall vote"
        )

        overall_votes = (
            filtered_profiles[
                "preferred_overall"
            ]
            .dropna()
            .astype(str)
            .map(format_coffee_label)
            .value_counts()
            .rename_axis("coffee_label")
            .reset_index(name="votes")
        )

        if overall_votes.empty:
            st.info(
                "No overall-vote data is available "
                "for the selected filters."
            )
        else:
            vote_chart = px.bar(
                overall_votes,
                x="coffee_label",
                y="votes",
                text_auto=True,
                category_orders={
                    "coffee_label": [
                        "Coffee A",
                        "Coffee B",
                        "Coffee C",
                        "Coffee D",
                    ]
                },
                labels={
                    (
                        "coffee_label"
                    ): "Coffee sample",
                    "votes": "Final votes",
                },
            )

            st.plotly_chart(
                vote_chart,
                use_container_width=True,
            )


def render_consumer_tab(
    filtered_profiles: pd.DataFrame,
) -> None:
    """Render consumer segmentation and spending analysis."""

    chart_1, chart_2 = st.columns(2)

    with chart_1:
        st.subheader(
            "Monthly coffee spending"
        )

        spending_distribution = (
            filtered_profiles[
                "monthly_coffee_spend"
            ]
            .value_counts()
            .reindex(SPENDING_ORDER)
            .fillna(0)
            .rename_axis(
                "monthly_coffee_spend"
            )
            .reset_index(
                name="respondents"
            )
        )

        spending_chart = px.bar(
            spending_distribution,
            x="monthly_coffee_spend",
            y="respondents",
            text_auto=True,
            labels={
                (
                    "monthly_coffee_spend"
                ): "Monthly spend",
                "respondents": "Respondents",
            },
        )

        st.plotly_chart(
            spending_chart,
            use_container_width=True,
        )

    with chart_2:
        st.subheader(
            "Preferred roast level"
        )

        roast_distribution = (
            filtered_profiles[
                "preferred_roast_level"
            ]
            .dropna()
            .value_counts()
            .rename_axis(
                "preferred_roast_level"
            )
            .reset_index(
                name="respondents"
            )
        )

        roast_chart = px.bar(
            roast_distribution,
            x="respondents",
            y="preferred_roast_level",
            orientation="h",
            text_auto=True,
            labels={
                (
                    "preferred_roast_level"
                ): "Roast level",
                "respondents": "Respondents",
            },
        )

        roast_chart.update_layout(
            yaxis={
                "categoryorder": (
                    "total ascending"
                ),
            }
        )

        st.plotly_chart(
            roast_chart,
            use_container_width=True,
        )

    st.info(
        create_spending_insight(
            filtered_profiles
        )
    )

    st.subheader(
        "Estimated spending by expertise segment"
    )

    spending_by_expertise = (
        filtered_profiles.dropna(
            subset=[
                "expertise_segment",
                "estimated_monthly_spend",
            ]
        )
        .groupby(
            "expertise_segment",
            as_index=False,
        )
        .agg(
            respondents=(
                "submission_id",
                "nunique",
            ),
            estimated_average_monthly_spend=(
                "estimated_monthly_spend",
                "mean",
            ),
            premium_customer_rate=(
                "is_premium_customer",
                "mean",
            ),
        )
    )

    spending_by_expertise[
        "premium_customer_rate"
    ] *= 100

    spending_by_expertise[
        "expertise_segment"
    ] = pd.Categorical(
        spending_by_expertise[
            "expertise_segment"
        ],
        categories=EXPERTISE_ORDER,
        ordered=True,
    )

    spending_by_expertise = (
        spending_by_expertise.sort_values(
            "expertise_segment"
        )
    )

    expertise_spending_chart = px.bar(
        spending_by_expertise,
        x="expertise_segment",
        y="estimated_average_monthly_spend",
        text_auto="$.0f",
        custom_data=[
            "respondents",
            "premium_customer_rate",
        ],
        labels={
            (
                "expertise_segment"
            ): "Expertise segment",
            (
                "estimated_average_monthly_spend"
            ): "Estimated monthly spend ($)",
        },
    )

    expertise_spending_chart.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Estimated average spend: "
            "$%{y:.0f}<br>"
            "Respondents: "
            "%{customdata[0]:,.0f}<br>"
            "Premium-customer rate: "
            "%{customdata[1]:.1f}%"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        expertise_spending_chart,
        use_container_width=True,
    )

    st.caption(
        "Spending values are estimates derived from "
        "survey spending bands. They are intended for "
        "segment comparison, not exact financial reporting."
    )


def render_data_tab(
    filtered_profiles: pd.DataFrame,
    filtered_performance: pd.DataFrame,
) -> None:
    """Render supporting data and methodology notes."""

    st.subheader(
        "Filtered coffee performance"
    )

    display_columns = [
        "coffee_label",
        "completed_ratings",
        "average_preference",
        "average_bitterness",
        "average_acidity",
        "preference_standard_deviation",
    ]

    display_data = (
        filtered_performance[
            display_columns
        ]
        .rename(
            columns={
                "coffee_label": "Coffee",
                (
                    "completed_ratings"
                ): "Completed ratings",
                (
                    "average_preference"
                ): "Average preference",
                (
                    "average_bitterness"
                ): "Average bitterness",
                (
                    "average_acidity"
                ): "Average acidity",
                (
                    "preference_standard_deviation"
                ): "Preference standard deviation",
            }
        )
        .round(2)
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander(
        "View filtered respondent data"
    ):
        st.dataframe(
            filtered_profiles,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Methodology notes")

    st.markdown(
        """
        - Preference, bitterness, and acidity are reported on
          1–5 survey scales.
        - Expertise is self-reported on a 1–10 scale.
        - Expertise segments are defined as Beginner (1–3),
          Intermediate (4–6), Advanced (7–8), and Expert (9–10).
        - Missing ratings are excluded from averages.
        - Estimated spending is derived from categorical monthly
          spending bands and is not an exact monetary value.
        - Premium customers are defined for this project as
          respondents with expertise of at least 7 and reported
          monthly spending of at least $60.
        - Results are observational and should not be interpreted
          as evidence that expertise causes a particular preference.
        """
    )


def main() -> None:
    """Render the complete Streamlit dashboard."""

    try:
        datasets = load_data()
    except FileNotFoundError as error:
        st.error(
            "Dashboard data could not be loaded. "
            "Run scripts/export_dashboard_data.py first."
        )
        st.code(str(error))
        st.stop()
    except pd.errors.ParserError as error:
        st.error(
            "A dashboard CSV could not be parsed."
        )
        st.code(str(error))
        st.stop()

    respondent_profile = datasets[
        "respondent_profile"
    ]

    taste_tests = datasets[
        "taste_tests"
    ]

    overall_performance = datasets[
        "coffee_performance"
    ].copy()

    overall_performance["coffee_label"] = (
        overall_performance["coffee_code"]
        .map(format_coffee_label)
    )

    total_dataset_respondents = (
        respondent_profile[
            "submission_id"
        ].nunique()
    )

    st.title(
        "☕ Coffee Enthusiasts"
    )

    st.markdown(
        "An interactive analysis of consumer profiles, "
        "spending patterns, coffee expertise, and blind "
        f"taste-test results from **"
        f"{total_dataset_respondents:,} survey respondents**."
    )

    (
        selected_age_groups,
        selected_expertise_segments,
    ) = render_sidebar(
        respondent_profile
    )

    filtered_profiles = respondent_profile[
        respondent_profile["age"]
        .astype(str)
        .isin(selected_age_groups)
        & respondent_profile[
            "expertise_segment"
        ].isin(
            selected_expertise_segments
        )
    ].copy()

    if filtered_profiles.empty:
        st.warning(
            "No respondents match the selected filters."
        )
        st.stop()

    filtered_ids = set(
        filtered_profiles[
            "submission_id"
        ].tolist()
    )

    filtered_taste_tests = taste_tests[
        taste_tests[
            "submission_id"
        ].isin(filtered_ids)
    ].copy()

    if filtered_taste_tests.empty:
        st.warning(
            "The selected respondents have no "
            "taste-test records."
        )
        st.stop()

    filtered_performance = (
        calculate_coffee_performance(
            filtered_taste_tests
        )
    )

    (
        overview_tab,
        taste_tab,
        consumer_tab,
        data_tab,
    ) = st.tabs(
        [
            "Executive overview",
            "Taste and expertise",
            "Consumer segments",
            "Data and methodology",
        ]
    )

    with overview_tab:
        render_overview_tab(
            filtered_profiles=filtered_profiles,
            filtered_taste_tests=filtered_taste_tests,
            filtered_performance=filtered_performance,
            overall_performance=overall_performance,
        )

    with taste_tab:
        render_taste_tab(
            filtered_profiles=filtered_profiles,
            filtered_taste_tests=filtered_taste_tests,
            filtered_performance=filtered_performance,
        )

    with consumer_tab:
        render_consumer_tab(
            filtered_profiles
        )

    with data_tab:
        render_data_tab(
            filtered_profiles=filtered_profiles,
            filtered_performance=filtered_performance,
        )

    st.divider()

    st.caption(
        "Coffee Enthusiasts portfolio project · "
        "Python ETL · SQLite · SQL analytical views · "
        "Streamlit"
    )


if __name__ == "__main__":
    main()