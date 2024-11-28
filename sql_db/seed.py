from faker import Faker
from psycopg2 import Error, connect
import random

from users_table import DB_CONFIG

faker = Faker(locale='uk_UA')

NUM_USERS = 10
NUM_TASKS = 30

STATUS_VALUES = [("new",), ("in progress",), ("completed",)]

def seed_db ():
    try:
        connection = connect(**DB_CONFIG)
        connection.autocommit = True

        cursor = connection.cursor()
        cursor.execute("TRUNCATE tasks RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE users RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE status RESTART IDENTITY CASCADE;")
        print("Таблиці очищено.")

        cursor.executemany('INSERT INTO status (name) VALUES (%s);', STATUS_VALUES)
        print("Таблиця 'status' заповнена.")

        user_data = [(faker.name(), faker.unique.email()) for _ in range(NUM_USERS)]
        cursor.executemany('INSERT INTO users (fullname, email) VALUES (%s, %s);', user_data)
        print(f"Таблиця 'users' заповнена {NUM_USERS} записами.")

        cursor.execute("SELECT id FROM users;")
        user_ids = [row[0] for row in cursor.fetchall()]
        if not user_ids:
            raise ValueError("Таблиця 'users' порожня. Неможливо створити завдання без користувачів.")
        else:
            print(f"Знайдено {len(user_ids)} користувачів: {user_ids}")

        cursor.execute("SELECT id FROM status;")
        status_ids = [row[0] for row in cursor.fetchall()]
        if not status_ids:
            raise ValueError("Таблиця 'status' порожня. Неможливо створити завдання без статусів.")
        else:
            print(f"Знайдено {len(status_ids)} статусів: {status_ids}")

        tasks_data = []
        for _ in range(NUM_TASKS):
            status_id = random.choice(status_ids)  
            user_id = random.choice(user_ids)      
    
            print(f"Додається завдання: status_id={status_id}, user_id={user_id}")
    
            tasks_data.append((
                faker.sentence(nb_words=4),       
                faker.text(max_nb_chars=200),    
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