import sqlite3
import pandas as pd


class DatabaseHandler:

    def __init__(self):

        self.conn = sqlite3.connect(
            'mood_bot.db',
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self.create_tables()

    def create_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reminder_time TEXT DEFAULT '21:00'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            entry_date TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            study_work_hours REAL NOT NULL,
            sleep_hours REAL NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

        self.conn.commit()

    def execute_query(self, query, params=None, fetch=False):

        cursor = self.conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:

            rows = cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]

        self.conn.commit()

    def get_or_create_user(
        self,
        user_id,
        username,
        first_name,
        last_name
    ):

        query = """
        INSERT OR IGNORE INTO users
        (
            user_id,
            username,
            first_name,
            last_name
        )
        VALUES (?, ?, ?, ?)
        """

        self.execute_query(
            query,
            (
                user_id,
                username,
                first_name,
                last_name
            )
        )

    def entry_exists(self, user_id, entry_date):

        query = """
        SELECT *
        FROM mood_entries
        WHERE user_id = ?
        AND entry_date = ?
        """

        result = self.execute_query(
            query,
            (
                user_id,
                str(entry_date)
            ),
            fetch=True
        )

        return len(result) > 0

    def save_mood_entry(
        self,
        user_id,
        entry_date,
        mood_score,
        study_work_hours,
        sleep_hours,
        comment
    ):

        query = """
        INSERT INTO mood_entries
        (
            user_id,
            entry_date,
            mood_score,
            study_work_hours,
            sleep_hours,
            comment
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """

        self.execute_query(
            query,
            (
                user_id,
                str(entry_date),
                mood_score,
                study_work_hours,
                sleep_hours,
                comment
            )
        )

    def get_all_user_entries(self, user_id):

        query = """
        SELECT *
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY entry_date DESC
        """

        return self.execute_query(
            query,
            (user_id,),
            fetch=True
        )

    def clear_user_data(self, user_id):

        query = """
        DELETE FROM mood_entries
        WHERE user_id = ?
        """

        self.execute_query(
            query,
            (user_id,)
        )

    def update_reminder_time(self, user_id, reminder_time):

        query = """
        UPDATE users
        SET reminder_time = ?
        WHERE user_id = ?
        """

        self.execute_query(
            query,
            (
                reminder_time,
                user_id
            )
        )

    def get_statistics_period(self, user_id, period):

        days = 7 if period == 'week' else 30

        query = f"""
        SELECT
            ROUND(AVG(mood_score), 2) as avg_mood,
            MIN(mood_score) as min_mood,
            MAX(mood_score) as max_mood,
            ROUND(AVG(study_work_hours), 2) as avg_work,
            ROUND(AVG(sleep_hours), 2) as avg_sleep,
            COUNT(*) as total_days
        FROM mood_entries
        WHERE user_id = ?
        AND date(entry_date) >= date('now', '-{days} day')
        """

        result = self.execute_query(
            query,
            (user_id,),
            fetch=True
        )

        return result[0]

    def get_dataframe(self, user_id):

        query = """
        SELECT *
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY entry_date
        """

        data = self.execute_query(
            query,
            (user_id,),
            fetch=True
        )

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        df['entry_date'] = pd.to_datetime(
            df['entry_date']
        )

        return df

    def get_insights(self, user_id):

        df = self.get_dataframe(user_id)

        if df.empty or len(df) < 5:

            return {
                "message": "Недостаточно данных для анализа"
            }

        insights = {}

        best_sleep = df.groupby(
            'sleep_hours'
        )['mood_score'].mean().idxmax()

        insights['best_sleep'] = (
            f"Лучшее настроение при сне "
            f"{best_sleep} ч"
        )

        best_work = df.groupby(
            'study_work_hours'
        )['mood_score'].mean().idxmax()

        insights['best_work'] = (
            f"Лучшее настроение при "
            f"{best_work} ч работы/учебы"
        )

        heavy_work = df[
            df['study_work_hours'] >= 7
        ]

        if not heavy_work.empty:

            avg_heavy_mood = heavy_work[
                'mood_score'
            ].mean()

            if avg_heavy_mood < 3:

                insights['work_effect'] = (
                    "Долгая работа/учеба "
                    "может ухудшать настроение"
                )

        df['weekday'] = df[
            'entry_date'
        ].dt.day_name()

        best_day = df.groupby(
            'weekday'
        )['mood_score'].mean().idxmax()

        insights['best_day'] = (
            f"Лучшее настроение чаще "
            f"всего в {best_day}"
        )

        return insights