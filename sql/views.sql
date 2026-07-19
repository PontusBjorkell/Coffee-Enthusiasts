-- ============================================================
-- COFFEE ENTHUSIASTS
-- ANALYTICAL SQLITE VIEWS
--
-- These views provide reusable reporting layers for the
-- Streamlit dashboard and SQL analysis.
-- ============================================================


-- ------------------------------------------------------------
-- One row per respondent with common analytical attributes
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_respondent_profile;

CREATE VIEW vw_respondent_profile AS
SELECT
    p.submission_id,
    p.age,
    p.gender,
    p.education_level,
    p.employment_status,
    p.number_children,
    p.work_from_home,

    h.cups_per_day,
    h.where_drink,
    h.brew_methods,
    h.purchase_locations,
    h.favorite_drink,
    h.preferred_style,
    h.preferred_strength,
    h.preferred_roast_level,
    h.caffeine_preference,
    h.expertise,
    h.likes_coffee_taste,
    h.knows_coffee_source,

    CASE
        WHEN h.expertise BETWEEN 1 AND 3
            THEN 'Beginner'
        WHEN h.expertise BETWEEN 4 AND 6
            THEN 'Intermediate'
        WHEN h.expertise BETWEEN 7 AND 8
            THEN 'Advanced'
        WHEN h.expertise BETWEEN 9 AND 10
            THEN 'Expert'
        ELSE 'Unknown'
    END AS expertise_segment,

    CASE
        WHEN h.expertise BETWEEN 1 AND 3
            THEN 1
        WHEN h.expertise BETWEEN 4 AND 6
            THEN 2
        WHEN h.expertise BETWEEN 7 AND 8
            THEN 3
        WHEN h.expertise BETWEEN 9 AND 10
            THEN 4
        ELSE 5
    END AS expertise_segment_order,

    s.monthly_coffee_spend,
    s.monthly_spend_band_order,
    s.estimated_monthly_spend,
    s.most_paid_for_coffee,
    s.most_willing_to_pay,
    s.cafe_coffee_good_value,
    s.equipment_spend,
    s.equipment_good_value,

    CASE
        WHEN
            h.expertise >= 7
            AND s.monthly_spend_band_order >= 4
        THEN 1
        ELSE 0
    END AS is_premium_customer,

    o.preferred_abc,
    o.preferred_a_or_d,
    o.preferred_overall

FROM participants AS p

LEFT JOIN coffee_habits AS h
    ON p.submission_id = h.submission_id

LEFT JOIN spending AS s
    ON p.submission_id = s.submission_id

LEFT JOIN overall_preferences AS o
    ON p.submission_id = o.submission_id;


-- ------------------------------------------------------------
-- One row per respondent and blind-tasted coffee
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_taste_test_analysis;

CREATE VIEW vw_taste_test_analysis AS
SELECT
    t.submission_id,
    t.coffee_code,
    t.bitterness,
    t.acidity,
    t.personal_preference,
    t.tasting_notes,

    r.age,
    r.gender,
    r.work_from_home,
    r.cups_per_day,
    r.preferred_roast_level,
    r.expertise,
    r.expertise_segment,
    r.expertise_segment_order,
    r.monthly_coffee_spend,
    r.monthly_spend_band_order,
    r.estimated_monthly_spend,
    r.is_premium_customer,
    r.preferred_overall

FROM taste_tests AS t

LEFT JOIN vw_respondent_profile AS r
    ON t.submission_id = r.submission_id;


-- ------------------------------------------------------------
-- One row per blind-tasted coffee
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_coffee_performance;

CREATE VIEW vw_coffee_performance AS
SELECT
    coffee_code,

    COUNT(
        personal_preference
    ) AS completed_ratings,

    ROUND(
        AVG(personal_preference),
        3
    ) AS average_preference,

    ROUND(
        AVG(bitterness),
        3
    ) AS average_bitterness,

    ROUND(
        AVG(acidity),
        3
    ) AS average_acidity,

    ROUND(
        AVG(
            personal_preference
            * personal_preference
        )
        - AVG(personal_preference)
        * AVG(personal_preference),
        3
    ) AS preference_variance

FROM taste_tests

GROUP BY coffee_code;


-- ------------------------------------------------------------
-- One row per expertise segment
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_expertise_summary;

CREATE VIEW vw_expertise_summary AS
SELECT
    expertise_segment,
    expertise_segment_order,

    COUNT(*) AS respondents,

    ROUND(
        AVG(expertise),
        3
    ) AS average_expertise,

    ROUND(
        AVG(estimated_monthly_spend),
        2
    ) AS estimated_average_monthly_spend,

    SUM(
        is_premium_customer
    ) AS premium_customers,

    ROUND(
        100.0
        * SUM(is_premium_customer)
        / COUNT(*),
        1
    ) AS premium_customer_percentage

FROM vw_respondent_profile

WHERE expertise_segment != 'Unknown'

GROUP BY
    expertise_segment,
    expertise_segment_order;


-- ------------------------------------------------------------
-- Preference performance by expertise segment and coffee
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_segment_coffee_performance;

CREATE VIEW vw_segment_coffee_performance AS
SELECT
    expertise_segment,
    expertise_segment_order,
    coffee_code,

    COUNT(
        personal_preference
    ) AS completed_ratings,

    ROUND(
        AVG(personal_preference),
        3
    ) AS average_preference,

    ROUND(
        AVG(bitterness),
        3
    ) AS average_bitterness,

    ROUND(
        AVG(acidity),
        3
    ) AS average_acidity

FROM vw_taste_test_analysis

WHERE expertise_segment != 'Unknown'

GROUP BY
    expertise_segment,
    expertise_segment_order,
    coffee_code;