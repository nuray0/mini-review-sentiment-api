# Mini Review Sentiment API

Простой HTTP-сервис на Flask, который принимает отзывы, определяет их настроение (`positive`, `negative`, `neutral`) и сохраняет в SQLite.

## Установка и запуск

```bash
pip install flask
python app.py
```

## Примеры для теста

### POST /reviews
```bash
curl -X POST "http://127.0.0.1:5000/reviews" \
  -H "Content-Type: application/json" \
  -d '{"text": "не    люблю этот сервис"}'
```

### Ожидаемый ответ:
```bash
{
  "created_at": "2025-07-09T13:22:46.967731",
  "id": 20,
  "sentiment": "negative",
  "text": "\u043d\u0435    \u043b\u044e\u0431\u043b\u044e \u044d\u0442\u043e\u0442 \u0441\u0435\u0440\u0432\u0438\u0441"
}
```

### GET /reviews?sentiment=negative
```bash
curl "http://127.0.0.1:5000/reviews?sentiment=negative"
```

### Ожидаемый ответ:
```bash
[
  {
    "created_at": "2025-07-09T12:36:16.270424",
    "id": 2,
    "sentiment": "negative",
    "text": "не нравится"
  },
  {
    "created_at": "2025-07-09T12:33:07.538710",
    "id": 1,
    "sentiment": "negative",
    "text": "сервис тупит"
  }
]
```

## При первом запуске создаётся reviews.db с таблицей reviews:
<pre><code class="language-sql">CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  sentiment TEXT NOT NULL,
  created_at TEXT NOT NULL
);
</code></pre>

## Что можно улучшить:

- Использовать ML или NLP-библиотеки для более точного определения тональности.
- Добавить поддержку разных языков и автоматическое определение языка отзыва.
- Добавить пагинацию и лимиты в GET /reviews.
- Написать автотесты для логики и API.
- Собрать в Docker-контейнер для удобства запуска.
- Добавить обработку ошибок и валидацию входных данных.