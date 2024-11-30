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

    def fetch_asks_by_satus(self, status_name):
        pass