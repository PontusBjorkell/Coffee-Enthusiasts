# Coffee Enthusiasts

**An end-to-end data analytics project exploring how coffee expertise relates to consumer behaviour, spending, sensory perception, and blind taste-test preferences.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **Live dashboard:** Add the Streamlit Community Cloud URL here after deployment.

<!-- Replace this placeholder after adding a screenshot. -->
<!--
![Coffee Enthusiasts dashboard](assets/dashboard-overview.png)
-->

## Project overview

Coffee Enthusiasts is a professional portfolio project built from a
survey and blind taste-test dataset containing 4,042 responses and
57 source variables.

The project demonstrates a complete analytics workflow:

- source-data validation and transformation with Python;
- normalization of a flat survey into a relational data model;
- storage and analysis in SQLite;
- 20 business-focused SQL queries;
- reusable analytical SQL views;
- automated CSV exports;
- an interactive Streamlit dashboard;
- reproducible, version-controlled project organization.

The central analytical question is:

> **Do people with greater coffee expertise evaluate blind-tasted
> coffees differently from less experienced coffee drinkers?**

## Business relevance

Understanding differences between novice and experienced consumers
can help coffee roasters, cafés, and retailers:

- identify commercially useful customer segments;
- evaluate product appeal across expertise levels;
- compare sensory preferences for different coffee samples;
- understand how engagement relates to spending;
- improve product positioning and targeted marketing;
- identify groups with stronger premium-customer potential.

## Analytics architecture

```text
Raw coffee survey CSV
          │
          ▼
Python validation and ETL
scripts/prepare_data.py
          │
          ├──────────────► Processed CSV tables
          │
          ▼
Normalized SQLite database
data/coffee_enthusiasts.db
          │
          ├──────────────► 20 SQL analyses
          │                 sql/analysis_queries.sql
          │
          ▼
Reusable analytical views
sql/views.sql
          │
          ▼
Dashboard-ready CSV exports
data/dashboard/
          │
          ▼
Interactive Streamlit dashboard
dashboard/app.py
```

## Dashboard

The Streamlit dashboard provides four analytical sections:

### Executive overview

- filtered respondent count;
- average self-reported expertise;
- highest-rated coffee;
- estimated monthly coffee spending;
- preference performance by sample;
- respondent distribution by expertise.

### Taste and expertise

- preference scores by expertise segment;
- acidity and bitterness comparisons;
- final overall coffee vote;
- sample sizes and descriptive interpretation.

### Consumer segments

- monthly spending distribution;
- preferred roast levels;
- estimated spending by expertise;
- premium-customer rates.

### Data and methodology

- filtered analytical tables;
- metric definitions;
- segmentation rules;
- assumptions and limitations.

## Data model

The raw survey is normalized into five tables.

| Table | Grain | Purpose |
|---|---|---|
| `participants` | One row per respondent | Demographics and employment characteristics |
| `coffee_habits` | One row per respondent | Consumption, brewing, preferences, and expertise |
| `spending` | One row per respondent | Coffee and equipment spending information |
| `taste_tests` | One row per respondent and coffee sample | Preference, acidity, bitterness, and tasting notes |
| `overall_preferences` | One row per respondent | Final comparisons and overall choice |

The `taste_tests` table converts four sets of Coffee A-D columns from
the original wide survey into a long analytical structure.

```text
participants
     │
     ├──── coffee_habits
     ├──── spending
     ├──── overall_preferences
     │
     └──── taste_tests
             ├── Coffee A
             ├── Coffee B
             ├── Coffee C
             └── Coffee D
```

## Analytical views

The SQLite reporting layer contains:

| View | Purpose |
|---|---|
| `vw_respondent_profile` | Respondent-level profile with reusable segmentation and spending fields |
| `vw_taste_test_analysis` | Taste-test records enriched with respondent attributes |
| `vw_coffee_performance` | Overall metrics for Coffees A-D |
| `vw_expertise_summary` | Respondent and spending metrics by expertise segment |
| `vw_segment_coffee_performance` | Preference and sensory metrics by expertise and coffee |

## Business questions

The SQL analysis contains 20 questions organized into five areas:

1. **Executive KPIs**
   - How many respondents are represented?
   - What is the average self-reported expertise?
   - How complete are the blind taste-test ratings?

2. **Consumer profile**
   - What are the major age and expertise groups?
   - Which roast levels are preferred?
   - How do working arrangements relate to coffee habits?

3. **Coffee performance**
   - Which coffee has the highest average preference?
   - How are ratings distributed?
   - Which sample is most acidic, bitter, or polarizing?
   - Which coffee wins the final vote?

4. **Expertise and taste**
   - How do preference scores vary by expertise?
   - Do sensory perceptions vary by expertise?
   - Which coffee wins within each expertise segment?

5. **Commercial insights**
   - How is monthly spending distributed?
   - Does estimated spending increase with expertise?
   - Which segments contain the strongest premium-customer groups?

## Expertise segments

Self-reported expertise is grouped as follows:

| Segment | Expertise score |
|---|---:|
| Beginner | 1-3 |
| Intermediate | 4-6 |
| Advanced | 7-8 |
| Expert | 9-10 |

The segmentation logic is defined once in the analytical view layer
and reused throughout the SQL analysis and dashboard.

## Spending methodology

Monthly coffee spending is recorded as categorical survey ranges rather
than exact amounts.

For comparison across groups, the project assigns a documented
representative value to each band:

| Spending band | Estimated value |
|---|---:|
| `<$20` | $10 |
| `$20-$40` | $30 |
| `$40-$60` | $50 |
| `$60-$80` | $70 |
| `$80-$100` | $90 |
| `>$100` | $110 |

These values are estimates for segment-level comparison. They must not
be interpreted as exact respondent spending or formal financial data.

A premium customer is defined within this project as a respondent who:

1. reports coffee expertise of at least 7; and
2. reports monthly coffee spending of at least $60.

## Repository structure

```text
Coffee-Enthusiasts/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   │   └── coffee_taste_test.csv
│   ├── processed/
│   │   ├── participants.csv
│   │   ├── coffee_habits.csv
│   │   ├── spending.csv
│   │   ├── taste_tests.csv
│   │   └── overall_preferences.csv
│   ├── analysis_results/
│   ├── dashboard/
│   └── coffee_enthusiasts.db
│
├── scripts/
│   ├── prepare_data.py
│   ├── create_views.py
│   ├── run_analysis.py
│   └── export_dashboard_data.py
│
├── sql/
│   ├── schema.sql
│   ├── analysis_queries.sql
│   └── views.sql
│
├── .streamlit/
│   └── config.toml
│
├── do-coffee-enthusiasts-taste-coffee-differently.ipynb
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Running the project locally

### 1. Clone the repository

```bash
git clone https://github.com/PontusBjorkell/Coffee-Enthusiasts.git
cd Coffee-Enthusiasts
```

### 2. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the ETL pipeline

```bash
python scripts/prepare_data.py
```

This command:

- validates the raw survey;
- creates five processed tables;
- writes processed CSV files;
- rebuilds the SQLite database;
- validates row counts, foreign keys, and database integrity.

### 5. Create the analytical views

```bash
python scripts/create_views.py
```

### 6. Run the SQL analysis

```bash
python scripts/run_analysis.py
```

The results are exported to:

```text
data/analysis_results/
```

### 7. Export dashboard data

```bash
python scripts/export_dashboard_data.py
```

### 8. Launch the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

## Deployment

The dashboard is designed for Streamlit Community Cloud.

Recommended deployment settings:

- **Repository:** `PontusBjorkell/Coffee-Enthusiasts`
- **Branch:** `main`
- **Main file path:** `dashboard/app.py`

The dashboard reads committed CSV files from `data/dashboard/`, so the
deployed application does not need to rebuild the SQLite database.

Before deployment:

```bash
python scripts/prepare_data.py
python scripts/create_views.py
python scripts/export_dashboard_data.py
git add .
git commit -m "Prepare Streamlit dashboard deployment"
git push
```

## Original exploratory analysis

The project began as a notebook exploring the central research
question and performing statistical analysis.

The notebook includes methods such as:

- exploratory data analysis;
- missing-value analysis;
- Friedman tests;
- Wilcoxon signed-rank tests;
- Kruskal-Wallis tests;
- Spearman correlation;
- consumer segmentation.

See:

[`do-coffee-enthusiasts-taste-coffee-differently.ipynb`](do-coffee-enthusiasts-taste-coffee-differently.ipynb)

The production-style ETL, SQL, database, and dashboard components were
developed as an extension of that initial analysis.

## Limitations

- Expertise is self-reported and may not reflect objectively measured skill.
- Spending is categorical and estimated values are approximate.
- Survey participants may not be representative of the wider coffee market.
- Missing ratings are excluded from averages.
- Descriptive dashboard differences do not automatically imply statistical significance.
- Observational relationships should not be interpreted as causal.
- Some survey fields contain multi-select text and would require additional normalization for more detailed behavioural analysis.

## Skills demonstrated

- Python data validation and ETL
- pandas transformation workflows
- relational data modeling
- SQLite database development
- SQL joins, CTEs, window functions, and views
- analytical metric design
- business-focused consumer segmentation
- Plotly visualization
- Streamlit dashboard development
- Git and GitHub version control
- reproducible project organization
- technical and business documentation

## Data source

The project uses the Coffee Taste Test Survey dataset that formed the
basis of the original notebook.

Before redistributing the raw data, confirm and document:

- the original publisher;
- the source URL;
- the dataset license;
- any redistribution restrictions.

## Author

**Pontus Björkell**

Data analytics portfolio project.