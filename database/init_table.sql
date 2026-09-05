DROP TABLE IF EXISTS chapters;

DROP TABLE IF EXISTS sections;

DROP TABLE IF EXISTS book_to_genre;

DROP TABLE IF EXISTS genres;

DROP TABLE IF EXISTS book_to_tag;

DROP TABLE IF EXISTS tags;

DROP TABLE IF EXISTS books;

DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(16) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    login VARCHAR(32) NOT NULL UNIQUE,
    nickname VARCHAR(32) NOT NULL UNIQUE,
    hashed_password VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NULL REFERENCES users (id) ON DELETE SET NULL,
    title VARCHAR(64) NOT NULL,
    description TEXT NULL,
    published_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_author_id on books (author_id);

CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book_to_genre (
    book_id INTEGER REFERENCES books (id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book_to_tag (
    book_id INTEGER REFERENCES books (id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, tag_id)
);

CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books (id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,
    previous_section_id INTEGER NULL
);

CREATE INDEX idx_book_sections on sections (book_id);

CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL REFERENCES sections (id),
    title VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    previous_chapter_id INTEGER NULL REFERENCES chapters (id) ON DELETE SET NULL DEFAULT NULL,
    next_chapter_id INTEGER NULL REFERENCES chapters (id) ON DELETE SET NULL DEFAULT NULL,
    position INTEGER NOT NULL
);

CREATE INDEX idx_section_chapters on chapters (section_id);