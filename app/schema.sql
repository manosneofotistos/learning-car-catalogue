-- CHECKPOINT 7 — Create the application database and seed it. 
-- Store the catalogue's editable content.
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY,

    name TEXT NOT NULL
        CHECK(length(trim(name)) BETWEEN 2 AND 80),

    category TEXT NOT NULL
        CHECK(category IN (
            'Hatchback',
            'Sedan',
            'SUV',
            'Coupe'
        )),

    manufacturer TEXT NOT NULL
        CHECK(length(trim(manufacturer)) BETWEEN 2 AND 60),

    variant TEXT NOT NULL
        CHECK(length(trim(variant)) BETWEEN 3 AND 120),

    description TEXT NOT NULL
        CHECK(length(trim(description)) BETWEEN 20 AND 1000),

    tip TEXT NOT NULL
        CHECK(length(trim(tip)) BETWEEN 5 AND 200)
);

-- CHECKPOINT 12 — Membership in the shared shortlist.
CREATE TABLE IF NOT EXISTS shortlist (
    car_id INTEGER PRIMARY KEY
        REFERENCES cars(id) ON DELETE CASCADE
);

-- Record whether initial sample data has already been inserted.
CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
);

