-- ============================================================
-- COFFEE ENTHUSIASTS: POWER BI ANALYTICAL VIEWS
-- Database: SQLite
-- ============================================================


-- ------------------------------------------------------------
-- One row per respondent with frequently used attributes
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
        WHEN h.expertise BETWEEN 1 AND 3 THEN 'Beginner'
        WHEN h.expertise BETWEEN 4 AND 6 THEN 'Intermediate'
        WHEN h.expertise BETWEEN 7 AND 8 THEN 'Advanced'
        WHEN h.expertise BETWEEN 9 AND 10 THEN 'Expert'
        ELSE 'Unknown'
    END AS expertise_segment,

    s.monthly_coffee_spend,
    s.most_paid_for_coffee,
    s.most_willing_to_pay,
    s.cafe_coffee_good_value,
    s.equipment_spend,
    s.equipment_good_value,

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
-- One row per respondent and tasted coffee
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

    p.age,
    p.gender,
    p.work_from_home,

    h.cups_per_day,
    h.preferred_roast_level,
    h.expertise,

    CASE
        WHEN h.expertise BETWEEN 1 AND 3 THEN 'Beginner'
        WHEN h.expertise BETWEEN 4 AND 6 THEN 'Intermediate'
        WHEN h.expertise BETWEEN 7 AND 8 THEN 'Advanced'
        WHEN h.expertise BETWEEN 9 AND 10 THEN 'Expert'
        ELSE 'Unknown'
    END AS expertise_segment,

    s.monthly_coffee_spend,

    o.preferred_overall

FROM taste_tests AS t

LEFT JOIN participants AS p
    ON t.submission_id = p.submission_id

LEFT JOIN coffee_habits AS h
    ON t.submission_id = h.submission_id

LEFT JOIN spending AS s
    ON t.submission_id = s.submission_id

LEFT JOIN overall_preferences AS o
    ON t.submission_id = o.submission_id;


-- ------------------------------------------------------------
-- Summary table for the four blind-tasted coffees
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_coffee_performance;

CREATE VIEW vw_coffee_performance AS
SELECT
    coffee_code,

    COUNT(personal_preference) AS completed_ratings,

    ROUND(
        AVG(personal_preference),
        2
    ) AS average_preference,

    ROUND(
        AVG(bitterness),
        2
    ) AS average_bitterness,

    ROUND(
        AVG(acidity),
        2
    ) AS average_acidity,

    ROUND(
        AVG(personal_preference * personal_preference)
        - AVG(personal_preference)
        * AVG(personal_preference),
        3
    ) AS preference_variance

FROM taste_tests

GROUP BY coffee_code;


-- ------------------------------------------------------------
-- Expertise segment summary for dashboard KPI cards
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_expertise_summary;

CREATE VIEW vw_expertise_summary AS
SELECT
    CASE
        WHEN expertise BETWEEN 1 AND 3 THEN 'Beginner'
        WHEN expertise BETWEEN 4 AND 6 THEN 'Intermediate'
        WHEN expertise BETWEEN 7 AND 8 THEN 'Advanced'
        WHEN expertise BETWEEN 9 AND 10 THEN 'Expert'
        ELSE 'Unknown'
    END AS expertise_segment,

    COUNT(*) AS respondents,

    ROUND(
        AVG(expertise),
        2
    ) AS average_expertise

FROM coffee_habits

GROUP BY expertise_segment;