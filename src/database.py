import sqlite3
import os


class Database:
    def __init__(self):
        # Путь к папке data относительно корня проект
        data_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data')

        # Путь к файлу базы данных
        self.db_path = os.path.join(data_path, 'levels.sqlite')

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"База данных не найдена: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Создаем таблицу, если её нет
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                current_level INTEGER DEFAULT 1,
                blood INTEGER DEFAULT 0,
                speed INTEGER DEFAULT 6,
                stealth INTEGER DEFAULT 100
            )
        ''')

        # Проверяем существующие столбцы
        columns = self.cursor.execute('PRAGMA table_info(user)').fetchall()
        existing_columns = [column[1] for column in columns]

        # Добавляем недостающие столбцы
        if 'blood' not in existing_columns:
            self.cursor.execute(
                'ALTER TABLE user ADD COLUMN blood INTEGER DEFAULT 0')
        if 'speed' not in existing_columns:
            self.cursor.execute(
                'ALTER TABLE user ADD COLUMN speed INTEGER DEFAULT 6')
        if 'stealth' not in existing_columns:
            self.cursor.execute(
                'ALTER TABLE user ADD COLUMN stealth INTEGER DEFAULT 100')

        self.conn.commit()

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

    def delete_save(self, user_id):
        """Удаляет сохранение по user_id"""
        try:
            self.cursor.execute('DELETE FROM user WHERE id = ?', (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении сохранения: {e}")
            return False

    def get_current_level(self, user_id):
        self.cursor.execute(
            'SELECT current_level FROM user WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 1

    def upgrade_stat(self, user_id, stat_name, cost):
        """Улучшает характеристику, если хватает крови"""
        try:
            # Проверяем количество крови
            self.cursor.execute(
                'SELECT blood FROM user WHERE id = ?', (user_id,))
            current_blood = self.cursor.fetchone()[0]

            if current_blood >= cost:
                # Отнимаем кровь и увеличиваем характеристику
                self.cursor.execute(f'''
                    UPDATE user 
                    SET blood = blood - ?,
                        {stat_name} = {stat_name} + ?
                    WHERE id = ?
                ''', (cost, 1, user_id))
                self.conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Ошибка при улучшении характеристики: {e}")
            return False

    def close(self):
        self.conn.close()
