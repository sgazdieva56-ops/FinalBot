CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reminder_time TEXT DEFAULT '21:00'
);

CREATE TABLE mood_entries (
    entry_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    mood_score INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 5),
    study_work_hours REAL NOT NULL,
    sleep_hours REAL NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);