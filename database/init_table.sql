DROP DATABASE IF EXISTS crossroads_db;

CREATE DATABASE crossroads_db;

\c crossroads_db

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(16) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    login VARCHAR(32) UNIQUE NOT NULL,
    nickname VARCHAR(32) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES users (id) ON DELETE SET NULL,
    title VARCHAR(64) NOT NULL,
    description TEXT NULL,
    published_at DATE
);

CREATE TABLE chapters (
    book_id INTEGER NOT NULL REFERENCES books (id) ON DELETE CASCADE,
    chapter_id INTEGER NOT NULL,
    title VARCHAR(16) NULL, --если есть нумерация глава 1, глава 2, то оставить NULL иначе NOT NULL
    content TEXT NOT NULL,
    PRIMARY KEY (book_id, chapter_id)
);