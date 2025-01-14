import sqlite3

# Назва файлу бази даних
DB_NAME = "bot_database.db"


# Ініціалізація бази даних
def init_db():
    """
    Ініціалізує базу даних: створює необхідні таблиці, якщо їх не існує.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Таблиця користувачів
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблиця логів навчання
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                hours REAL,
                note TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        conn.commit()


# Додавання нового користувача
def add_user(user_id, username):
    """
    Додає нового користувача до бази даних, якщо він ще не зареєстрований.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, username)
                VALUES (?, ?)
            """, (user_id, username))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Помилка при додаванні користувача: {e}")


# Збереження часу навчання
def log_learning_time(user_id, category, hours, note, date_added):
    """
    Зберігає лог навчання в базу даних.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO time_logs (user_id, category, hours, note, date_added)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, category, hours, note, date_added))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Помилка при збереженні часу навчання: {e}")


# Отримання статистики за категоріями
def get_category_stats(user_id):
    """
    Повертає кількість годин за кожною категорією для користувача.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(hours)
            FROM time_logs
            WHERE user_id = ?
            GROUP BY category
        """, (user_id,))
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}


# Отримання логів для обраної категорії
def get_logs_by_category(user_id, category):
    """
    Повертає всі логи для заданої категорії.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_added, hours, note
            FROM time_logs
            WHERE user_id = ? AND category = ?
            ORDER BY date_added DESC
        """, (user_id, category))
        rows = cursor.fetchall()
    return [{"date": row[0], "hours": row[1], "note": row[2]} for row in rows]


# Додаткова функція: видалення всіх логів (опціонально, для тестів)
def clear_all_logs():
    """
    Видаляє всі логи навчання з бази даних (для тестових цілей).
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM time_logs")
        conn.commit()


# Додаткова функція: видалення всіх користувачів (опціонально, для тестів)
def clear_all_users():
    """
    Видаляє всіх користувачів з бази даних (для тестових цілей).
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
