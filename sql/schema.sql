-- Coffee Enthusiasts portfolio project
-- SQLite relational database schema

PRAGMA foreign_keys = ON;

-- One row per survey respondent
CREATE TABLE IF NOT EXISTS participants (
    submission_id TEXT PRIMARY KEY,
    age TEXT,
    gender TEXT,
    gender_specify TEXT,
    education_level TEXT,
    ethnicity_race TEXT,
    ethnicity_race_specify TEXT,
    employment_status TEXT,
    number_children TEXT,
    political_affiliation TEXT,
    work_from_home TEXT
);

-- One row per respondent describing general coffee habits
CREATE TABLE IF NOT EXISTS coffee_habits (
    submission_id TEXT PRIMARY KEY,
    cups_per_day TEXT,
    where_drink TEXT,
    brew_methods TEXT,
    brew_other TEXT,
    purchase_locations TEXT,
    purchase_other TEXT,
    favorite_drink TEXT,
    favorite_specify TEXT,
    additions TEXT,
    additions_other TEXT,
    dairy TEXT,
    sweetener TEXT,
    preferred_style TEXT,
    preferred_strength TEXT,
    preferred_roast_level TEXT,
    caffeine_preference TEXT,
    expertise INTEGER,
    reasons_for_drinking TEXT,
    reasons_for_drinking_other TEXT,
    likes_coffee_taste TEXT,
    knows_coffee_source TEXT,

    FOREIGN KEY (submission_id)
        REFERENCES participants (submission_id)
        ON DELETE CASCADE
);

-- One row per respondent describing coffee spending
CREATE TABLE IF NOT EXISTS spending (
    submission_id TEXT PRIMARY KEY,
    monthly_coffee_spend TEXT,
    most_paid_for_coffee TEXT,
    most_willing_to_pay TEXT,
    cafe_coffee_good_value TEXT,
    equipment_spend TEXT,
    equipment_good_value TEXT,

    FOREIGN KEY (submission_id)
        REFERENCES participants (submission_id)
        ON DELETE CASCADE
);

-- Four rows per respondent: one for each blind-tasted coffee
CREATE TABLE IF NOT EXISTS taste_tests (
    submission_id TEXT NOT NULL,
    coffee_code TEXT NOT NULL,
    bitterness INTEGER,
    acidity INTEGER,
    personal_preference INTEGER,
    tasting_notes TEXT,

    PRIMARY KEY (submission_id, coffee_code),

    CHECK (coffee_code IN ('A', 'B', 'C', 'D')),
    CHECK (bitterness BETWEEN 1 AND 5 OR bitterness IS NULL),
    CHECK (acidity BETWEEN 1 AND 5 OR acidity IS NULL),
    CHECK (
        personal_preference BETWEEN 1 AND 5
        OR personal_preference IS NULL
    ),

    FOREIGN KEY (submission_id)
        REFERENCES participants (submission_id)
        ON DELETE CASCADE
);

-- One row per respondent summarizing comparisons between samples
CREATE TABLE IF NOT EXISTS overall_preferences (
    submission_id TEXT PRIMARY KEY,
    preferred_abc TEXT,
    preferred_a_or_d TEXT,
    preferred_overall TEXT,

    FOREIGN KEY (submission_id)
        REFERENCES participants (submission_id)
        ON DELETE CASCADE
);

-- Indexes make common analytical queries faster
CREATE INDEX IF NOT EXISTS idx_taste_tests_coffee
    ON taste_tests (coffee_code);

CREATE INDEX IF NOT EXISTS idx_habits_expertise
    ON coffee_habits (expertise);

CREATE INDEX IF NOT EXISTS idx_participants_age
    ON participants (age);