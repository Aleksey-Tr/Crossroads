INSERT INTO
    users (
        role,
        login,
        nickname,
        hashed_password
    )
VALUES (
        'admin',
        'admin_main',
        'Главный Админ',
        '$2b$12$LJ3m4ys3Gz0eXQZl8vYmPOeYXJz5vQZzF5eXQZl8vYmPOeYXJz5vQ'
    ),
    (
        'user',
        'reader_one',
        'Читатель Один',
        '$2b$12$Ab3m4ys3Gz0eXQZl8vYmPOeYXJz5vQZzF5eXQZl8vYmPOeYXJz5vQ'
    ),
    (
        'user',
        'author_jane',
        'Джейн Писатель',
        '$2b$12$Cd3m4ys3Gz0eXQZl8vYmPOeYXJz5vQZzF5eXQZl8vYmPOeYXJz5vQ'
    ),
    (
        'user',
        'author_mark',
        'Марк Рассказчик',
        '$2b$12$Ef3m4ys3Gz0eXQZl8vYmPOeYXJz5vQZzF5eXQZl8vYmPOeYXJz5vQ'
    ),
    (
        'user',
        'cyber_writer',
        'Кибер Автор',
        '$2b$12$Gh3m4ys3Gz0eXQZl8vYmPOeYXJz5vQZzF5eXQZl8vYmPOeYXJz5vQ'
    ),
    (
        'admin',
        'string',
        'string',
        '$2b$12$PFVS1aKu79Y/j8rFFtUubeDehHyXCfslzHz4whY6VkGzXwhVzk/EW'
    );
;

INSERT INTO
    books (author_id, title, description)
VALUES (
        (
            SELECT id
            FROM users
            WHERE
                login = 'author_jane'
        ),
        'Путь магии',
        'История юного мага, поступившего в Академию Света.'
    ),
    (
        (
            SELECT id
            FROM users
            WHERE
                login = 'author_jane'
        ),
        'Темный Лес',
        'Мистическая история о девушке в запретном лесу.'
    ),
    (
        (
            SELECT id
            FROM users
            WHERE
                login = 'author_mark'
        ),
        'Академия теней',
        'Детектив о расследовании исчезновения студента.'
    ),
    (
        (
            SELECT id
            FROM users
            WHERE
                login = 'cyber_writer'
        ),
        'Хроники киберпанка',
        'Киберпанк-триллер о хакере и мегакорпорациях.'
    ),
    (
        (
            SELECT id
            FROM users
            WHERE
                login = 'author_mark'
        ),
        'Пустой дом',
        'Хоррор о семье в доме с темным прошлым.'
    );

INSERT INTO
    genres (name)
VALUES ('Фэнтези'),
    ('Мистика'),
    ('Детектив'),
    ('Киберпанк'),
    ('Хоррор'),
    ('Приключения');

INSERT INTO
    book_to_genre (book_id, genre_id)
VALUES (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Фэнтези'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Приключения'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Темный Лес'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Мистика'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Темный Лес'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Приключения'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Детектив'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Мистика'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Хроники киберпанка'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Киберпанк'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Пустой дом'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Хоррор'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Пустой дом'
        ),
        (
            SELECT id
            FROM genres
            WHERE
                name = 'Мистика'
        )
    );

INSERT INTO
    tags (name)
VALUES ('магия'),
    ('академия'),
    ('выбор'),
    ('тайна'),
    ('будущее'),
    ('призраки'),
    ('расследование');

INSERT INTO
    book_to_tag (book_id, tag_id)
VALUES (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'магия'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'академия'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Темный Лес'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'тайна'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'академия'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'тайна'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'расследование'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Хроники киберпанка'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'будущее'
        )
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Пустой дом'
        ),
        (
            SELECT id
            FROM tags
            WHERE
                name = 'призраки'
        )
    );

INSERT INTO
    sections (
        book_id,
        name,
        previous_section_id
    )
VALUES (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        'Пролог: Письмо из академии',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        'Прибытие в Академию Света',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        'Первый урок магии',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        'Тайна старой библиотеки',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Путь магии'
        ),
        'Пробуждение древней силы',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Темный Лес'
        ),
        'Вход в Тёмный Лес',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Темный Лес'
        ),
        'Тропа к старому дубу',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Темный Лес'
        ),
        'Логово лесного зверя',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        'Исчезновение студента',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        'Расследование начинается',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Академия теней'
        ),
        'Разгадка тайны',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Хроники киберпанка'
        ),
        'Неоновый город',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Хроники киберпанка'
        ),
        'Задание от корпорации',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Хроники киберпанка'
        ),
        'Взлом главной системы',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Пустой дом'
        ),
        'Переезд',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Пустой дом'
        ),
        'Странные звуки ночью',
        NULL
    ),
    (
        (
            SELECT id
            FROM books
            WHERE
                title = 'Пустой дом'
        ),
        'Подвал',
        NULL
    );

UPDATE sections s
SET
    previous_section_id = (
        SELECT s2.id
        FROM sections s2
        WHERE
            s2.book_id = s.book_id
            AND s2.name = CASE s.name
                WHEN 'Прибытие в Академию Света' THEN 'Пролог: Письмо из академии'
                WHEN 'Первый урок магии' THEN 'Прибытие в Академию Света'
                WHEN 'Тайна старой библиотеки' THEN 'Первый урок магии'
                WHEN 'Пробуждение древней силы' THEN 'Тайна старой библиотеки'
                WHEN 'Тропа к старому дубу' THEN 'Вход в Тёмный Лес'
                WHEN 'Логово лесного зверя' THEN 'Тропа к старому дубу'
                WHEN 'Расследование начинается' THEN 'Исчезновение студента'
                WHEN 'Разгадка тайны' THEN 'Расследование начинается'
                WHEN 'Задание от корпорации' THEN 'Неоновый город'
                WHEN 'Взлом главной системы' THEN 'Задание от корпорации'
                WHEN 'Странные звуки ночью' THEN 'Переезд'
                WHEN 'Подвал' THEN 'Странные звуки ночью'
            END
    );

INSERT INTO
    chapters (
        section_id,
        title,
        content,
        position
    )
VALUES (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Пролог: Письмо из академии'
        ),
        'Письмо с золотой печатью',
        'Элиан держал в руках письмо с печатью Академии Света. Золотые чернила переливались в лучах утреннего солнца.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Пролог: Письмо из академии'
        ),
        'Прощание с домом',
        'Мама обняла его на пороге. "Ты готов, сынок?" Элиан кивнул, хотя внутри всё дрожало от волнения.',
        2
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Прибытие в Академию Света'
        ),
        'Белые башни',
        'Ворота Академии Света распахнулись перед Элианом. Башни из белого камня уходили в небо.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Первый урок магии'
        ),
        'Зажги свечу',
        'Мастер Орион начал урок с простого: зажечь свечу силой мысли. Элиан сосредоточился, и пламя вспыхнуло.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Первый урок магии'
        ),
        'Необычный талант',
        '"Необычный талант," — пробормотал мастер, пристально глядя на Элиана.',
        2
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Тайна старой библиотеки'
        ),
        'Запретная секция',
        'В библиотеке Элиан нашёл дверь, которую не замечал раньше. За ней скрывались книги на забытых языках.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Пробуждение древней силы'
        ),
        'Пробуждение силы',
        'Сила пробудилась внутри Элиана, как древний вулкан. Свет заполнил зал.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Вход в Тёмный Лес'
        ),
        'Кромка леса',
        'Лена стояла у кромки Тёмного Леса. Деревья были такими высокими, что вершины терялись в тумане.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Тропа к старому дубу'
        ),
        'Тихая тропа',
        'Тропа вела к старому дубу. Чем глубже Лена заходила, тем тише становилось вокруг.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Логово лесного зверя'
        ),
        'Следы в пещере',
        'У старого дуба Лена нашла логово лесного зверя. Огромные следы вели в пещеру.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Исчезновение студента'
        ),
        'Тень на стене',
        'Студент академии теней исчез бесследно. Последнее, что видели — его тень на стене коридора.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Расследование начинается'
        ),
        'Запретное крыло',
        'Мира опросила всех, кто видел исчезнувшего. Улики указывали на запретное крыло академии.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Разгадка тайны'
        ),
        'Другое измерение',
        'Студент нашёл древний артефакт, который переносил тени между мирами.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Неоновый город'
        ),
        'Город без сна',
        'Неоновый город никогда не спал. Рекламные голограммы освещали мокрые улицы.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Задание от корпорации'
        ),
        'Ночной звонок',
        'Звонок от корпорации "Нексус" поступил в три часа ночи. Задание: взломать систему конкурента.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Взлом главной системы'
        ),
        'Ловушка',
        'Взлом главной системы оказался ловушкой. Рейн понял это слишком поздно.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Переезд'
        ),
        'Новый дом',
        'Семья переехала в старый дом на окраине города. Риелтор уверял, что владельцы съехали внезапно.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Странные звуки ночью'
        ),
        'Шорох за стеной',
        'Ночью Аня услышала шорох за стеной. Будто кто-то скрёбся, пытаясь выбраться.',
        1
    ),
    (
        (
            SELECT id
            FROM sections
            WHERE
                name = 'Подвал'
        ),
        'То, что внизу',
        'Дверь подвала открылась сама. Внизу, в темноте, кто-то ждал.',
        1
    );

UPDATE chapters c1
SET
    next_chapter_id = (
        SELECT c2.id
        FROM chapters c2
        WHERE
            c2.section_id = c1.section_id
            AND c2.position = c1.position + 1
    );

UPDATE chapters c1
SET
    previous_chapter_id = (
        SELECT c2.id
        FROM chapters c2
        WHERE
            c2.section_id = c1.section_id
            AND c2.position = c1.position - 1
    );