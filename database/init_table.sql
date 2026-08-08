DROP DATABASE IF EXISTS novels_test_db;

CREATE DATABASE novels_test_db;

\c novels_test_db

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(16) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    login VARCHAR(32) UNIQUE NOT NULL,
    nickname VARCHAR(32) UNIQUE NOT NULL,
    password VARCHAR(16) NOT NULL, --только для тестов
    password_hash VARCHAR() NOT NULL
);

CREATE TABLE novels (
    id SERIAL PRIMARY KEY,
    author_id INTEGER FOREIGN KEY REFERENCES users (id) NOT NULL,
    title VARCHAR(64) NOT NULL,
    description TEXT NULL,
);

CREATE TABLE characters (
    novel_id INTEGER NOT NULL FOREIGN KEY REFERENCES novels (id),
    character_id INTEGER NOT NULL,
    title VARCHAR(16) NULL, --если есть нумерация глава 1, глава 2, то оставить NULL иначе NOT NULL
    content TEXT NOT NULL,
    PRIMARY KEY (novel_id, character_id)
);