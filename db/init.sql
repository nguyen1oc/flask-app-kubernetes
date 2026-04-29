CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    poll_id INT REFERENCES polls(id),
    text TEXT,
    votes INT DEFAULT 0
);