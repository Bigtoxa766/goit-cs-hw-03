import psycopg2

host = 'localhost'
port = 5433
user = 'postgres'
password = 'test'
dbname = 'postgres'

def user_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    );
    '''
    return create_table_query

def status_table():
    create_table_query = ''' 
    CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    );
    '''
    return create_table_query

def tasks_table():
    create_table_query = ''' 
    CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES status (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES status (id) ON DELETE CASCADE
    );
    '''
    return create_table_query

try:
    connection = psycopg2.connect(
        dbname=dbname, user = user, password = password,
        host = host, port = port
    )

    connection.autocommit = True
    cursor = connection.cursor()

    create_user_table = user_table()
    cursor.execute(create_user_table)
    print("Таблиця 'users' успішно створена.")

    create_status_table = status_table()
    cursor.execute(create_status_table)
    print("Таблиця 'status' успішно створена.")
    insert_values_query = '''
    INSERT INTO status (name) VALUES
        ('new'),
        ('in progress'),
        ('completed')
    ON CONFLICT (name) DO NOTHING;
    '''
    cursor.execute(insert_values_query)
    print("Початкові значення успішно вставлені.")

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