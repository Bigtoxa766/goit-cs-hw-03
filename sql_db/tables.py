import psycopg2

# Конфігурація бази даних
DB_CONFIG = {
'host': 'localhost',
'port': 5433,
'user': 'postgres',
'password': 'test',
'dbname': 'postgres'}

# Функція створення таблиці users
def user_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    );
    '''
    return create_table_query

# Функція створення таблиці status
def status_table():
    create_table_query = ''' 
    CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    );
    ''' 
    return create_table_query

# Функція створення таблиці tasks
def tasks_table():
    create_table_query = ''' 
    CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES status (id) ON DELETE CASCADE
    );
    '''
    return create_table_query

# Функція видалення таблиць
def drop_table_if_exists(table_name):
    return f"DROP TABLE IF EXISTS {table_name} CASCADE;"

try:
    # Підключення до БД
    connection = psycopg2.connect(**DB_CONFIG)

    connection.autocommit = True
    cursor = connection.cursor()

    # Видалення попередніх таблиць 
    cursor.execute(drop_table_if_exists('tasks'))
    cursor.execute(drop_table_if_exists('status'))
    cursor.execute(drop_table_if_exists('users'))

    # Створення таблиці users
    create_user_table = user_table()
    cursor.execute(create_user_table)
    print("Таблиця 'users' успішно створена.")

    # Створення таблиці status
    create_status_table = status_table()
    cursor.execute(create_status_table)
    print("Таблиця 'status' успішно створена.")

    # Створення таблиці tasks
    create_tasks_table = tasks_table()
    cursor.execute(create_tasks_table)
    print("Таблиця 'tasks' успішно створена.")

except Exception as e:
    print(f"Помилка при створенні таблиці: {e}")

finally:
    if connection:
        cursor.close()
        connection.close()
        print("З'єднання з PostgreSQL закрито.")