# Coffee Enthusiasts: Taste, Expertise, and Consumer Behaviour

## Project Overview

This project investigates whether experienced coffee drinkers evaluate coffee differently from less experienced consumers.

Using survey and blind taste-test data from more than 4,000 participants, the analysis examines coffee preferences, sensory perceptions, purchasing behaviour, and self-reported coffee expertise.

The central research question is:

> **Do people with greater coffee expertise evaluate blind-tasted coffees differently from less experienced coffee drinkers?**

## Business Relevance

Understanding how coffee expertise affects taste preferences can help coffee roasters, cafés, and retailers:

* identify meaningful customer segments;
* develop products for novice and experienced consumers;
* improve product positioning and marketing;
* understand how taste preferences relate to spending behaviour;
* determine whether specialty products appeal differently to highly engaged consumers.

## Dataset

The dataset contains 4,042 survey responses and 57 variables covering:

* demographic characteristics;
* daily coffee consumption;
* brewing and purchasing habits;
* roast and strength preferences;
* self-reported coffee expertise;
* monthly coffee spending;
* blind taste-test evaluations;
* perceived acidity and bitterness;
* preference ratings for Coffees A, B, C, and D.

## Research Questions

1. What does the typical participant’s coffee consumption profile look like?
2. Which blind-test coffee is preferred overall?
3. Are differences between the coffee ratings statistically significant?
4. Does coffee expertise influence blind taste preferences?
5. Do experienced consumers respond differently to acidity and bitterness?
6. Is coffee expertise associated with higher coffee spending?

## Tools and Methods

**Tools**

* Python
* pandas
* NumPy
* Matplotlib
* SciPy
* Jupyter Notebook

**Analytical methods**

* exploratory data analysis;
* missing-value analysis;
* data visualization;
* Friedman tests;
* Wilcoxon signed-rank tests;
* Kruskal–Wallis tests;
* Spearman correlation;
* consumer segmentation.

## Key Findings

* Coffee D achieved the highest average preference score, although it was also the most polarizing option.
* Coffee expertise was associated with meaningful differences in blind taste preferences.
* Experienced coffee drinkers evaluated sensory characteristics differently from less experienced participants.
* Greater coffee expertise was associated with higher monthly coffee spending.
* The results suggest that coffee expertise reflects both sensory experience and deeper engagement with coffee as a consumer category.

## Repository Structure

```text
Coffee-Enthusiasts/
│
├── README.md
├── notebooks/
│   └── coffee_enthusiasts_analysis.ipynb
├── data/
│   ├── raw/
│   └── processed/
├── sql/
├── powerbi/
└── images/
```

The SQL analysis, processed dataset, Power BI dashboard, and dashboard screenshots will be added as the project develops.

## Current Analysis

The complete exploratory and statistical analysis is available in the project notebook:

[`coffee_enthusiasts_analysis.ipynb`](notebooks/coffee_enthusiasts_analysis.ipynb)

## Planned Extensions

* prepare a clean analytical dataset;
* create a relational SQL database;
* write business-focused SQL queries;
* build an interactive Power BI dashboard;
* document business recommendations;
* add dashboard screenshots and data-model documentation.

## Data Source

Coffee Taste Test Survey dataset. The source and licensing information will be documented here before distributing the raw data.

## Author

**Pontus Björkell**

Data analytics portfolio project.
