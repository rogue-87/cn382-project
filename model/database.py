import sqlite3
from typing import Optional


class Database:
    db_path: str

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "model/database.db"

        # establish a temporary connection solely for checking
        # if tables exist in the database
        try:
            with sqlite3.connect(self.db_path) as connection:
                # enable foreign keys
                connection.execute("PRAGMA foreign_keys = ON")

                # create student table if it doesn't exist
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS student
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        isSuspended BOOLEAN DEFAULT 0
                    )
                    """
                )

                # create book table if it doesn't exist
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS book
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT,
                        description TEXT,
                        publishDate DATE,
                        isbn TEXT,
                        quantity INTEGER DEFAULT 1
                    )
                    """
                )

                ## create rental table if it doesn't exist
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rental
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        rental_start DATE NOT NULL,
                        rental_end DATE NOT NULL,
                        is_returned BOOLEAN DEFAULT 0,
                        FOREIGN KEY(student_id) REFERENCES student(id),
                        FOREIGN KEY(book_id) REFERENCES book(id)
                    )
                    """
                )

                # create notification table if it doesn't exist
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notification
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL,
                        user_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES student(id)
                    )
                    """
                )
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
