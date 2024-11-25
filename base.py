import sqlite3

class DatabaseManager:
    def __init__(self, db_name='minesweeper.db'):
        self.db_connection = sqlite3.connect(db_name)
        self.create_database()

    def create_database(self):
        """Создание таблицы scores, если она не существует"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                difficulty TEXT,
                time INTEGER
            )
        ''')
        self.db_connection.commit()

    def save_score(self, name, difficulty, time):
        """Сохранение результата игры"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO scores (player_name, difficulty, time)
            VALUES (?, ?, ?)
        ''', (name, difficulty, time))
        self.db_connection.commit()

    def get_recent_names(self, limit=3):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT DISTINCT player_name 
            FROM scores 
            ORDER BY id DESC 
            LIMIT ?
        ''', (limit,))
        return [row[0] for row in cursor.fetchall()]

    def get_records_by_difficulty(self, difficulty):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT player_name, time
            FROM scores 
            WHERE difficulty = ?
            ORDER BY time ASC
            LIMIT 3
        ''', (difficulty,))
        return cursor.fetchall()

    def close_connection(self):
        self.db_connection.close()
