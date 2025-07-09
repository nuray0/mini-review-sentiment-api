import re
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)
DB_NAME = 'reviews.db'

# Позитивные шаблоны: хорошо, отлично, прекрасно, итд
POSITIVE_PATTERNS = [
    r'\bхорош\w*',
    r'\bотличн\w*',
    r'\bпрекрасн\w*',
    r'\bзамечательн\w*',
    r'\bлюбл\w*',
    r'\b(по|)нрав\w*',
    r'\bсупер\b',
    r'\bшикарн\w*',
    r'\bудобн\w*',
    r'\bклассн\w*',
    r'\bне\s*плох\w*',
]

# Негативные шаблоны: плохо, ужасно, ненавижу, итд.
NEGATIVE_PATTERNS = [
    r'\b(?<!не)плох\w*',
    r'\bужасн\w*',
    r'\bненавиж\w*',
    r'\bне\s*работ\w*',
    r'\bпроблем\w*',
    r'\bразочар\w*',
    r'\bотстой\b',
    r'\bотврат\b',
    r'\bгадост\w*',
    r'\bтупит\w*',
    r'\bбесит\b',
    r'\bглюч\w*',
    r'\bне\s+коррект\w*',
]


def preceded_by_negation(text: str, start_idx: int) -> bool:
    """
    Проверяет, идёт ли отдельное слово 'не' непосредственно перед позитивным словом.
    Работает даже при нескольких пробелах: 'не    нравится'.
    """
    before = text[:start_idx]
    tokens = re.findall(r'\w+', before)
    return tokens and tokens[-1] == 'не'


def get_sentiment(text: str) -> str:
    text = text.lower()

    # Явный негатив — приоритетнее
    for pattern in NEGATIVE_PATTERNS:
        for match in re.finditer(pattern, text):
            start = match.start()
            # если перед "плох" стоит "не", то НЕ считать негативом
            if preceded_by_negation(text, start):
                continue
            return 'negative'

    # Позитив — только если перед ним нет "не"
    for pattern in POSITIVE_PATTERNS:
        for match in re.finditer(pattern, text):
            start = match.start()
            if preceded_by_negation(text, start):
                return 'negative'
            return 'positive'

    return 'neutral'


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text']
    sentiment = get_sentiment(text)
    created_at = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
        (text, sentiment, created_at),
    )
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify(
        {
            'id': review_id,
            'text': text,
            'sentiment': sentiment,
            'created_at': created_at,
        }
    )


@app.route('/reviews', methods=['GET'])
def get_reviews():
    sentiment = request.args.get('sentiment')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if sentiment:
        cursor.execute(
            'SELECT id, text, sentiment, created_at FROM reviews WHERE sentiment = ?',
            (sentiment,),
        )
    else:
        cursor.execute('SELECT id, text, sentiment, created_at FROM reviews')
    rows = cursor.fetchall()
    conn.close()

    result = [
        {
            'id': row[0],
            'text': row[1],
            'sentiment': row[2],
            'created_at': row[3],
        }
        for row in rows
    ]

    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
