from faker import Faker
from psycopg2 import connect
import random

from users_table import DB_CONFIG

faker = Faker(locale='uk_UA')

NUM_USERS = 10
NUM_TASKS = 30

def seed_db():
    try:
        connection = connect(**DB_CONFIG)
        connection.autocommit = True

        cursor = connection.cursor()
        # Очищення таблиць
        cursor.execute("TRUNCATE tasks RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE users RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE status RESTART IDENTITY CASCADE;")
        print("Таблиці очищено.")

        # Додавання записів у таблицю 'status'
        status_values = [('new',), ('in progress',), ('completed',)]
        cursor.executemany("INSERT INTO status (name) VALUES (%s);", status_values)
        print("Таблиця 'status' заповнена.")

        # Наповнення таблиці 'users'
        user_data = [(faker.name(), faker.unique.email()) for _ in range(NUM_USERS)]
        cursor.executemany('INSERT INTO users (fullname, email) VALUES (%s, %s);', user_data)
        print(f"Таблиця 'users' заповнена {NUM_USERS} записами.")

        # Знаходження id status
        cursor.execute("SELECT id FROM status;")
        status_ids = [row[0] for row in cursor.fetchall()]
        if not status_ids:
            raise ValueError("Таблиця 'status' порожня. Неможливо створити завдання без статусів.")
        print(f"Знайдено статуси: {status_ids}")

        # Знаходження id users
        cursor.execute("SELECT id FROM users;")
        user_ids = [row[0] for row in cursor.fetchall()]
        if not user_ids:
            raise ValueError("Таблиця 'users' порожня. Неможливо створити завдання без користувачів.")
        print(f"Знайдено користувачів: {user_ids}")

        # Наповнення таблиці tasks
        tasks_data = []
        for _ in range(NUM_TASKS):
            status_id = random.choice(status_ids)
            user_id = random.choice(user_ids)
            print(f"Додається завдання: status_id={status_id}, user_id={user_id}")
            tasks_data.append((
                faker.sentence(nb_words=4),  # title
                faker.text(max_nb_chars=200),  # description
                status_id,
                user_id
            ))
        cursor.executemany(
            "INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s);",
            tasks_data
        )
        print(f"Таблиця 'tasks' заповнена {NUM_TASKS} записами.")

    except Exception as e:
        print(f"Помилка при заповненні бази даних: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("З'єднання з PostgreSQL закрито.")

if __name__ == "__main__":
    seed_db()