import psycopg2
from tables import DB_CONFIG

class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True

        except psycopg2.Error as e:
            raise Exception (f"DatabaseManager помилка підключення до бази даних: {e}")
     
    def close(self):
        if self.connection:
            self.connection.close()

    def fetch_user_tasks(self, user_id):
        # Отримує всі завдання користувача за його id
        query = ''' 
        SELECT tasks.id, tasks.title, tasks.description, status.name AS
        status_name FROM tasks
        JOIN status ON tasks.status_id = status.id
        WHERE tasks.user_id = %s;
        '''
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                tasks = cursor.fetchall()

                return [{
                        'task_id': task[0],
                        'title': task[1],
                        'description': task[2],
                        'status': task[3]
                    } for task in tasks]
                
        except psycopg2.Error as e:
            raise Exception(f"DatabaseManager помилка виконання запиту: {e}")

    def fetch_tasks_by_status(self, status_name):
        # отримує завдання за певним статусом
        query = '''SELECT tasks.id, tasks.title, tasks.description, 
        status.name AS status_name FROM tasks 
        JOIN status ON tasks.status_id = status.id
        WHERE status.name = %s;'''
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (status_name,))
                tasks = cursor.fetchall()

                return [{
                    'task_id': task[0],
                    'title': task[1],
                    'description': task[2],
                    'status': task[3]
                } for task in tasks]
            
        except psycopg2.Error as e:
            raise Exception(f"DatabaseManager помилка виконання запиту: {e}")
        
    def update_task_status(self, task_id, new_status):
        # Оновлює статус конкретного завдання

        query = '''
        UPDATE tasks
        SET status_id = (SELECT id FROM status WHERE name = %s)
        WHERE id = %s
        RETURNING id, title, status_id'''

        get_status_name_query = 'SELECT name FROM status WHERE id = %s'

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (new_status, task_id))
                updated_task = cursor.fetchone()

                if updated_task is None:
                    raise Exception(f"Завдання з ID {task_id} не знайдено або статус '{new_status}' не існує.")
                
                cursor.execute(get_status_name_query, (updated_task[2],))
                status_name = cursor.fetchone()[0]
            
                return {
                    'task_id': updated_task[0],
                    'title': updated_task[1],
                    'new_status_id': updated_task[2],
                    'new_status': status_name,
                }
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def fetch_users_without_tasks(self):
        # Отримує список користувачів, які не мають жодного завдання

        query = '''SELECT id, fullname, email FROM users 
        WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks
        WHERE user_id IS NOT NULL);'''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()

                return [{
                    'user_id': user[0],
                    'fullname': user[1],
                    'email': user[2],
                } for user in users]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def add_task_for_user(self, user_id, title, description, status_name):
        # Додає нове завдання для конкретного користувача

        query = '''
        INSERT INTO tasks (title, description, status_id, user_id)
        VALUES (%s, %s, (SELECT id FROM status WHERE name = %s), %s)
        RETURNING id, title, description, status_id, user_id;
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (title, description, status_name, user_id))
                new_task = cursor.fetchone()

                if new_task is None:
                    raise Exception(f"Не вдалося створити завдання для користувача з ID {user_id}.")
                
                cursor.execute('SELECT name FROM status WHERE id = %s', (new_task[3],))
                status_name = cursor.fetchone()[0]

                return {
                    'task_id': new_task[0],
                    'title': new_task[1],
                    'description': new_task[2],
                    'status_id': new_task[3],
                    'status': status_name,
                    'user_id': new_task[4],
                }
        except psycopg2.Error as e:
            raise Exception (f"Помилка виконання запиту: {e}")
        
    def fetch_incomplete_tasks(self):
        # Отримує всі завдання, статус яких не є 'завершено'

        query = '''
        SELECT tasks.id, tasks.title, tasks.description, status.name AS status_name, tasks.user_id
        FROM tasks
        JOIN status ON tasks.status_id = status.id
        WHERE status.id != (SELECT id FROM status WHERE name = %s);
        '''

        try: 
            with self.connection.cursor() as cursor:
                cursor.execute(query, ('completed',))
                tasks = cursor.fetchall()

                return [{
                    'task_id': task[0],
                    'title': task[1],
                    'description': task[2],
                    'status': task[3],
                    'user_id': task[4]
                } for task in tasks]
            
        except psycopg2.Error as e:
            raise Exception (f"Помилка виконання запиту: {e}")
        
    def delete_task_by_id(self, task_id):
        # Видаляє завдання за його ID.

        query = '''
        DELETE FROM tasks
        WHERE id = %s
        RETURNING id, title, description;
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (task_id,))
                deleted_task = cursor.fetchone()

                if deleted_task is None:
                    raise Exception(f"Завдання з ID {task_id} не знайдено.")
                
                return {
                    'task_id': deleted_task[0],
                    'title': deleted_task[1],
                    'description': deleted_task[2],
                    'message': f"Завдання з ID {task_id} успішно видалено."
                }
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def find_users_by_email(self, email_pattern):
        # Знаходить користувачів за певною електронною поштою 

        query = '''
        SELECT id, fullname, email FROM users
        WHERE email LIKE %s
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (email_pattern,))
                users = cursor.fetchall()

                return [{
                   'user_id': user[0],
                    'fullname': user[1],
                    'email': user[2] 
                } for user in users]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def update_user_name(self, user_id, new_fullname):
        # Оновлює ім'я користувача у базі даних

        query = '''
        UPDATE users
        SET fullname = %s
        WHERE id = %s
        RETURNING id, fullname, email;'''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (new_fullname, user_id))
                updated_user = cursor.fetchone()

                if not updated_user:
                    raise Exception(f"Користувача з ID {user_id} не знайдено.")
                
                return {
                    'user_id': updated_user[0],
                    'fullname': updated_user[1],
                    'email': updated_user[2],
                    'message': f"Ім'я користувача з ID {user_id} успішно оновлено на '{new_fullname}'."
                }
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def count_tasks_by_status(self):
        # Отримує кількість завдань для кожного статусу

        query = '''
        SELECT status.name AS status_name, COUNT (tasks.id) AS task_count
        FROM status 
        LEFT JOIN tasks ON status.id = tasks.status_id
        GROUP BY status.name
        ORDER BY task_count DESC;'''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                status_counts = cursor.fetchall()

                return [{
                    'status_name': status[0],
                    'task_count': status[1]
                } for status in status_counts]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def fetch_tasks_by_email_domain(self, domain):
        # Отримує завдання, призначені користувачам із певною доменною частиною електронної пошти

        query = '''
        SELECT tasks.id AS task_id, tasks.title, tasks.description, 
        users.fullname, users.email 
        FROM tasks
        JOIN users ON tasks.user_id = users.id
        WHERE users.email LIKE %s'''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (f"%{domain}",))
                tasks = cursor.fetchall()

                return [{
                    'task_id': task[0],
                    'title': task[1],
                    'description': task[2],
                    'user_fullname': task[3],
                    'user_email': task[4]
                } for task in tasks]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def fetch_tasks_without_description(self):
        # Отримує список завдань, у яких відсутній опис

        query = '''
        SELECT id, title, status_id, user_id
        FROM tasks
        WHERE description IS NULL OR description = ''; '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                tasks = cursor.fetchall()

                return [{
                    'task_id': task[0],
                    'title': task[1],
                    'status_id': task[2],
                    'user_id': task[3]
                } for task in tasks]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def fetch_users_and_tasks_in_progress(self):
        # тримує список користувачів і їхніх завдань, які знаходяться у статусі 'in progress'

        query = '''
        SELECT users.id AS user_id, users.fullname, users.email,
        tasks.id AS task_id, tasks.title, tasks.description
        FROM users
        INNER JOIN tasks ON users.id = tasks.user_id
        INNER JOIN status ON tasks.status_id = status.id
        WHERE status.name = 'in progress';'''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                res = cursor.fetchall()

                return[{
                    'user_id': row[0],
                    'fullname': row[1],
                    'email': row[2],
                    'task_id': row[3],
                    'task_title': row[4],
                    'task_description': row[5], 
                } for row in res]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")
        
    def fetch_users_and_task_counts(self):
        # Отримує список користувачів і кількість їхніх завдань

        query = '''
        SELECT users.id AS user_id, users.fullname, users.email, 
        COUNT(tasks.id) AS task_count
        FROM users
        LEFT JOIN tasks ON users.id = tasks.user_id
        GROUP BY users.id, users.fullname, users.email
        ORDER BY task_count DESC;
        '''
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

                return [{
                    'user_id': row[0],
                    'fullname': row[1],
                    'email': row[2],
                    'task_count': row[3]
                } for row in results]
        except psycopg2.Error as e:
            raise Exception(f"Помилка виконання запиту: {e}")