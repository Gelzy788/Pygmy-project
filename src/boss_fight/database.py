import sqlite3
import os


class Database:
    def __init__(self):
        # Путь к папке data относительно корня проекта
        data_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))), 'data')

        # Путь к файлу базы данных
        self.db_path = os.path.join(data_path, 'levels.sqlite')

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"База данных не найдена: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def get_all_saves(self):
        self.cursor.execute(
            'SELECT id, username FROM user ORDER BY id')
        saves = self.cursor.fetchall()
        # Возвращаем только первые 5 сохранений
        return saves[:5]

    def create_save(self, nickname):
        self.cursor.execute(
            'INSERT INTO user (username) VALUES (?)', (nickname,))
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_save(self, save_id):
        self.cursor.execute('DELETE FROM user WHERE id = ?', (save_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
