DROP DATABASE IF EXISTS crossroads_db;

CREATE DATABASE crossroads_db;

\c crossroads_db

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(16) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    login VARCHAR(32) NOT NULL UNIQUE,
    nickname VARCHAR(32) NOT NULL UNIQUE,
    hashed_password VARCHAR(256) NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NULL REFERENCES users (id) ON DELETE SET NULL,
    title VARCHAR(64) NOT NULL,
    description TEXT NULL,
    published_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE book_to_genre (
    book_id INTEGER REFERENCES books (id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE book_to_tag (
    book_id INTEGER REFERENCES books (id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, tag_id)
);

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books (id) ON DELETE CASCADE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    previous_section INTEGER NULL REFERENCES sections (id) ON DELETE SET NULL,
    title VARCHAR(256) NOT NULL
);

CREATE INDEX idx_first_sections ON sections (book_id)
WHERE
    previous_section IS NULL;

CREATE UNIQUE INDEX idx_one_first_default_per_book ON sections (book_id)
where
    previous_section IS NULL
    AND is_default = TRUE;

CREATE UNIQUE INDEX idx_one_default_per_section ON sections (previous_section)
where
    is_default = TRUE
    AND previous_section IS NOT NULL;

CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL REFERENCES sections (id),
    title VARCHAR(64) NOT NULL,
    content TEXT NOT NULL
);