INSERT INTO users (user_id, username, first_name)
VALUES
(1, 'testuser', 'Test');

INSERT INTO mood_entries
(
    user_id,
    entry_date,
    mood_score,
    study_work_hours,
    sleep_hours,
    comment
)
VALUES
(1, CURRENT_DATE - INTERVAL '14 day', 4, 5, 8, 'Хороший день'),
(1, CURRENT_DATE - INTERVAL '13 day', 3, 6, 7, 'Устал'),
(1, CURRENT_DATE - INTERVAL '12 day', 5, 4, 9, 'Отлично'),
(1, CURRENT_DATE - INTERVAL '11 day', 2, 8, 5, 'Мало сна'),
(1, CURRENT_DATE - INTERVAL '10 day', 4, 5, 8, 'Нормально'),
(1, CURRENT_DATE - INTERVAL '9 day', 5, 3, 9, 'Супер'),
(1, CURRENT_DATE - INTERVAL '8 day', 3, 7, 6, 'Тяжело'),
(1, CURRENT_DATE - INTERVAL '7 day', 4, 4, 8, 'Спокойно'),
(1, CURRENT_DATE - INTERVAL '6 day', 5, 2, 9, 'Выспался'),
(1, CURRENT_DATE - INTERVAL '5 day', 2, 9, 5, 'Устал'),
(1, CURRENT_DATE - INTERVAL '4 day', 3, 6, 7, 'Средне'),
(1, CURRENT_DATE - INTERVAL '3 day', 4, 5, 8, 'Хорошо'),
(1, CURRENT_DATE - INTERVAL '2 day', 5, 3, 9, 'Отличный день'),
(1, CURRENT_DATE - INTERVAL '1 day', 4, 4, 8, 'Неплохо');