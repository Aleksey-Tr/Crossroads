INSERT INTO
    users (
        role,
        login,
        nickname,
        password,
        password_hash
    )
VALUES
    -- Администраторы
    (
        'admin',
        'admin_main',
        'Главраг',
        'admin123',
        '$2b$12$EixZaYVK1V6M1k73uQz1O.7W42vX9W6i6K6F7b8c9d0e1f2g3h4i5'
    ),
    (
        'admin',
        'moderator_01',
        'Следопыт',
        'mod987',
        '$2b$12$KixZaYVK1V6M1k73uQz1O.7W42vX9W6i6K6F7b8c9d0e1f2g3h4i6'
    ),
    (
        'user',
        'alex_smith',
        'Алекс',
        'qwerty2026',
        '$2b$12$MixZaYVK1V6M1k73uQz1O.7W42vX9W6i6K6F7b8c9d0e1f2g3h4i7'
    ),
    (
        'user',
        'elena_book',
        'Книголюб',
        'elena_pass',
        '$2b$12$NixZaYVK1V6M1k73uQz1O.7W42vX9W6i6K6F7b8c9d0e1f2g3h4i8'
    ),
    (
        'user',
        'reader_99',
        'Чтец Снов',
        'shadow77',
        '$2b$12$OixZaYVK1V6M1k73uQz1O.7W42vX9W6i6K6F7b8c9d0e1f2g3h4i9'
    );

INSERT INTO
    books (
        author_id,
        title,
        description,
        published_at
    )
VALUES (
        3,
        'Путь магии',
        'Захватывающее фэнтези о молодом волшебнике.',
        '2026-01-15'
    ),
    (
        3,
        'Темный Лес',
        'Продолжение приключений в неизведанных землях.',
        '2026-05-20'
    ),
    (
        4,
        'Академия теней',
        'Детективный роман в антураже магической школы.',
        '2025-11-02'
    ),
    (
        5,
        'Хроники киберпанка',
        'Антиутопия о мире корпораций и неоновых улиц.',
        '2026-07-01'
    );