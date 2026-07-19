-- ============================================================
-- COFFEE ENTHUSIASTS: BUSINESS ANALYSIS
-- Database: SQLite
--
-- Purpose:
-- Analyse coffee preferences, consumer behaviour, expertise,
-- taste-test performance, and spending patterns.
-- ============================================================


-- ============================================================
-- SECTION 1: EXECUTIVE KPIs
-- ============================================================


-- 1. How many survey respondents are represented?
SELECT
    COUNT(*) AS total_respondents
FROM participants;


-- 2. What is the average self-reported coffee expertise?
SELECT
    ROUND(AVG(expertise), 2) AS average_expertise,
    MIN(expertise) AS minimum_expertise,
    MAX(expertise) AS maximum_expertise,
    COUNT(expertise) AS respondents_with_expertise
FROM coffee_habits;


-- 3. How many respondents completed each coffee taste test?
SELECT
    coffee_code,
    COUNT(personal_preference) AS completed_ratings,
    ROUND(
        100.0 * COUNT(personal_preference)
        / COUNT(DISTINCT submission_id),
        1
    ) AS completion_rate_percent
FROM taste_tests
GROUP BY coffee_code
ORDER BY coffee_code;


-- 4. Which roast level is most popular?
SELECT
    preferred_roast_level,
    COUNT(*) AS respondents,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        1
    ) AS percentage
FROM coffee_habits
WHERE preferred_roast_level IS NOT NULL
GROUP BY preferred_roast_level
ORDER BY respondents DESC;


-- 5. How many cups of coffee do respondents drink each day?
SELECT
    cups_per_day,
    COUNT(*) AS respondents,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        1
    ) AS percentage
FROM coffee_habits
WHERE cups_per_day IS NOT NULL
GROUP BY cups_per_day
ORDER BY
    CASE cups_per_day
        WHEN 'Less than 1' THEN 0
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4' THEN 4
        WHEN 'More than 4' THEN 5
        ELSE 6
    END;


-- ============================================================
-- SECTION 2: CONSUMER SEGMENTS
-- ============================================================


-- 6. What is the age distribution of respondents?
SELECT
    age,
    COUNT(*) AS respondents,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        1
    ) AS percentage
FROM participants
WHERE age IS NOT NULL
GROUP BY age
ORDER BY
    CASE age
        WHEN '<18 years old' THEN 1
        WHEN '18-24 years old' THEN 2
        WHEN '25-34 years old' THEN 3
        WHEN '35-44 years old' THEN 4
        WHEN '45-54 years old' THEN 5
        WHEN '55-64 years old' THEN 6
        WHEN '>65 years old' THEN 7
        ELSE 8
    END;


-- 7. How does average coffee expertise vary by age?
SELECT
    p.age,
    COUNT(h.expertise) AS respondents,
    ROUND(AVG(h.expertise), 2) AS average_expertise
FROM participants AS p
JOIN coffee_habits AS h
    ON p.submission_id = h.submission_id
WHERE
    p.age IS NOT NULL
    AND h.expertise IS NOT NULL
GROUP BY p.age
ORDER BY
    CASE p.age
        WHEN '<18 years old' THEN 1
        WHEN '18-24 years old' THEN 2
        WHEN '25-34 years old' THEN 3
        WHEN '35-44 years old' THEN 4
        WHEN '45-54 years old' THEN 5
        WHEN '55-64 years old' THEN 6
        WHEN '>65 years old' THEN 7
        ELSE 8
    END;


-- 8. Which roast level is preferred by each expertise segment?
WITH expertise_segments AS (
    SELECT
        submission_id,
        preferred_roast_level,
        CASE
            WHEN expertise BETWEEN 1 AND 3 THEN 'Beginner'
            WHEN expertise BETWEEN 4 AND 6 THEN 'Intermediate'
            WHEN expertise BETWEEN 7 AND 8 THEN 'Advanced'
            WHEN expertise BETWEEN 9 AND 10 THEN 'Expert'
        END AS expertise_segment
    FROM coffee_habits
    WHERE
        expertise IS NOT NULL
        AND preferred_roast_level IS NOT NULL
)
SELECT
    expertise_segment,
    preferred_roast_level,
    COUNT(*) AS respondents,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (
            PARTITION BY expertise_segment
        ),
        1
    ) AS segment_percentage
FROM expertise_segments
GROUP BY
    expertise_segment,
    preferred_roast_level
ORDER BY
    CASE expertise_segment
        WHEN 'Beginner' THEN 1
        WHEN 'Intermediate' THEN 2
        WHEN 'Advanced' THEN 3
        WHEN 'Expert' THEN 4
    END,
    respondents DESC;


-- 9. Does working location relate to coffee consumption?
SELECT
    p.work_from_home,
    h.cups_per_day,
    COUNT(*) AS respondents
FROM participants AS p
JOIN coffee_habits AS h
    ON p.submission_id = h.submission_id
WHERE
    p.work_from_home IS NOT NULL
    AND h.cups_per_day IS NOT NULL
GROUP BY
    p.work_from_home,
    h.cups_per_day
ORDER BY
    p.work_from_home,
    respondents DESC;


-- ============================================================
-- SECTION 3: BLIND TASTE-TEST PERFORMANCE
-- ============================================================


-- 10. Which coffee received the highest average preference score?
SELECT
    coffee_code,
    COUNT(personal_preference) AS completed_ratings,
    ROUND(AVG(personal_preference), 2) AS average_preference
FROM taste_tests
WHERE personal_preference IS NOT NULL
GROUP BY coffee_code
ORDER BY average_preference DESC;


-- 11. How were preference ratings distributed for each coffee?
SELECT
    coffee_code,
    personal_preference,
    COUNT(*) AS rating_count,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (
            PARTITION BY coffee_code
        ),
        1
    ) AS percentage_within_coffee
FROM taste_tests
WHERE personal_preference IS NOT NULL
GROUP BY
    coffee_code,
    personal_preference
ORDER BY
    coffee_code,
    personal_preference;


-- 12. Which coffee was perceived as most bitter and most acidic?
SELECT
    coffee_code,
    ROUND(AVG(bitterness), 2) AS average_bitterness,
    ROUND(AVG(acidity), 2) AS average_acidity
FROM taste_tests
GROUP BY coffee_code
ORDER BY coffee_code;


-- 13. Which coffee was the most polarizing?
--
-- Variance is used as a measure of disagreement:
-- a higher value means ratings were more spread out.
SELECT
    coffee_code,
    ROUND(AVG(personal_preference), 2) AS average_preference,
    ROUND(
        AVG(personal_preference * personal_preference)
        - AVG(personal_preference) * AVG(personal_preference),
        3
    ) AS preference_variance
FROM taste_tests
WHERE personal_preference IS NOT NULL
GROUP BY coffee_code
ORDER BY preference_variance DESC;


-- 14. Which coffee won the final overall vote?
SELECT
    preferred_overall,
    COUNT(*) AS votes,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        1
    ) AS vote_percentage
FROM overall_preferences
WHERE preferred_overall IS NOT NULL
GROUP BY preferred_overall
ORDER BY votes DESC;


-- ============================================================
-- SECTION 4: EXPERTISE AND TASTE
-- ============================================================


-- 15. How do preference scores differ by expertise segment?
SELECT
    expertise_segment,
    coffee_code,
    completed_ratings,
    ROUND(
        average_preference,
        2
    ) AS average_preference
FROM vw_segment_coffee_performance
ORDER BY
    expertise_segment_order,
    coffee_code;


-- 16. How do acidity and bitterness perceptions vary by expertise?
SELECT
    expertise_segment,
    coffee_code,
    ROUND(
        average_bitterness,
        2
    ) AS average_bitterness,
    ROUND(
        average_acidity,
        2
    ) AS average_acidity
FROM vw_segment_coffee_performance
ORDER BY
    expertise_segment_order,
    coffee_code;


-- 17. Which coffee was selected overall by each expertise segment?
SELECT
    expertise_segment,
    preferred_overall,
    COUNT(*) AS votes,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (
            PARTITION BY expertise_segment
        ),
        1
    ) AS segment_vote_percentage
FROM vw_respondent_profile
WHERE
    expertise_segment != 'Unknown'
    AND preferred_overall IS NOT NULL
GROUP BY
    expertise_segment,
    expertise_segment_order,
    preferred_overall
ORDER BY
    expertise_segment_order,
    votes DESC;


-- ============================================================
-- SECTION 5: SPENDING AND COMMERCIAL INSIGHTS
-- ============================================================


-- 18. What is the distribution of monthly coffee spending?
SELECT
    monthly_coffee_spend,
    monthly_spend_band_order,
    COUNT(*) AS respondents,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (),
        1
    ) AS percentage
FROM vw_respondent_profile
WHERE monthly_coffee_spend IS NOT NULL
GROUP BY
    monthly_coffee_spend,
    monthly_spend_band_order
ORDER BY monthly_spend_band_order;


-- 19. Do more experienced consumers spend more each month?
SELECT
    expertise_segment,
    expertise_segment_order,

    COUNT(
        estimated_monthly_spend
    ) AS respondents_with_spending_data,

    ROUND(
        AVG(estimated_monthly_spend),
        2
    ) AS estimated_average_monthly_spend,

    ROUND(
        AVG(
            CASE
                WHEN monthly_spend_band_order >= 4
                    THEN 1.0
                ELSE 0.0
            END
        ) * 100.0,
        1
    ) AS percentage_spending_at_least_60

FROM vw_respondent_profile

WHERE
    expertise_segment != 'Unknown'
    AND estimated_monthly_spend IS NOT NULL

GROUP BY
    expertise_segment,
    expertise_segment_order

ORDER BY expertise_segment_order;


-- 20. Which groups are the strongest potential premium customers?
--
-- Premium customers are defined as respondents who:
--   1. Report expertise of 7 or higher; and
--   2. Report monthly coffee spending of at least $60.
SELECT
    age,
    preferred_roast_level,

    COUNT(*) AS respondents,

    SUM(
        is_premium_customer
    ) AS premium_customer_count,

    ROUND(
        100.0
        * SUM(is_premium_customer)
        / COUNT(*),
        1
    ) AS premium_customer_rate

FROM vw_respondent_profile

WHERE
    age IS NOT NULL
    AND preferred_roast_level IS NOT NULL

GROUP BY
    age,
    preferred_roast_level

HAVING
    COUNT(*) >= 20
    AND SUM(is_premium_customer) >= 5

ORDER BY
    premium_customer_count DESC,
    premium_customer_rate DESC;