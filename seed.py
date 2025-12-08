#!/usr/bin/env python3
"""
Seed script to populate the database with sample data.
Run this script to add initial books, students, and rentals.
"""

import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from model.database import Database


def seed_database():
    db = Database()
    conn = db.connect()

    try:
        cur = conn.cursor()

        # Seed students
        students = [
            ("Alice Johnson", "alice@example.com", "password123"),
            ("Bob Smith", "bob@example.com", "password123"),
            ("Charlie Brown", "charlie@example.com", "password123"),
            ("Diana Prince", "diana@example.com", "password123"),
            ("Eve Wilson", "eve@example.com", "password123"),
        ]

        print("Seeding students...")
        for name, email, password in students:
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT OR IGNORE INTO student (name, email, password, isSuspended) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, False),
            )

        # Seed books
        books = [
            (
                "The Great Gatsby",
                "F. Scott Fitzgerald",
                "A classic American novel about the Jazz Age.",
                "1925-04-10",
                "978-0-7432-7356-5",
                3,
            ),
            (
                "To Kill a Mockingbird",
                "Harper Lee",
                "A gripping tale of racial injustice and childhood innocence.",
                "1960-07-11",
                "978-0-06-112008-4",
                2,
            ),
            (
                "1984",
                "George Orwell",
                "A dystopian social science fiction novel.",
                "1949-06-08",
                "978-0-452-28423-4",
                4,
            ),
            (
                "Pride and Prejudice",
                "Jane Austen",
                "A romantic novel of manners.",
                "1813-01-28",
                "978-0-14-143951-8",
                2,
            ),
            (
                "The Catcher in the Rye",
                "J.D. Salinger",
                "A controversial novel about teenage rebellion.",
                "1951-07-16",
                "978-0-316-76948-0",
                3,
            ),
            (
                "Harry Potter and the Philosopher's Stone",
                "J.K. Rowling",
                "The first book in the Harry Potter series.",
                "1997-06-26",
                "978-0-7475-3269-9",
                5,
            ),
            (
                "The Lord of the Rings",
                "J.R.R. Tolkien",
                "An epic fantasy adventure.",
                "1954-07-29",
                "978-0-544-00203-5",
                2,
            ),
            (
                "Dune",
                "Frank Herbert",
                "A science fiction epic set on the desert planet Arrakis.",
                "1965-08-01",
                "978-0-441-17271-9",
                3,
            ),
        ]

        print("Seeding books...")
        for title, author, description, publish_date, isbn, quantity in books:
            cur.execute(
                "INSERT OR IGNORE INTO book (title, author, description, publishDate, isbn, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, description, publish_date, isbn, quantity),
            )

        # Get student and book IDs for rentals
        cur.execute("SELECT id FROM student")
        student_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT id FROM book")
        book_ids = [row[0] for row in cur.fetchall()]

        # Seed some rentals
        rentals = [
            (
                student_ids[0],
                book_ids[0],
                datetime.now().date() - timedelta(days=5),
                datetime.now().date() + timedelta(days=2),
                False,
            ),  # Active
            (
                student_ids[1],
                book_ids[1],
                datetime.now().date() - timedelta(days=10),
                datetime.now().date() - timedelta(days=3),
                True,
            ),  # Returned
            (
                student_ids[2],
                book_ids[2],
                datetime.now().date() - timedelta(days=2),
                datetime.now().date() + timedelta(days=5),
                False,
            ),  # Active
            (
                student_ids[3],
                book_ids[3],
                datetime.now().date() - timedelta(days=15),
                datetime.now().date() - timedelta(days=8),
                True,
            ),  # Returned
            (
                student_ids[4],
                book_ids[4],
                datetime.now().date() - timedelta(days=1),
                datetime.now().date() + timedelta(days=6),
                False,
            ),  # Active
        ]

        print("Seeding rentals...")
        for student_id, book_id, start_date, end_date, is_returned in rentals:
            cur.execute(
                "INSERT OR IGNORE INTO rental (student_id, book_id, rental_start, rental_end, is_returned) VALUES (?, ?, ?, ?, ?)",
                (student_id, book_id, start_date, end_date, is_returned),
            )

        # Seed some notifications
        notifications = [
            ("Your rental for 'The Great Gatsby' is due in 2 days.", student_ids[0]),
            ("Welcome to the library system!", student_ids[1]),
            ("Your account has been suspended due to overdue books.", student_ids[2]),
            ("Reminder: Return 'To Kill a Mockingbird' by tomorrow.", student_ids[3]),
        ]

        print("Seeding notifications...")
        for message, user_id in notifications:
            cur.execute(
                "INSERT OR IGNORE INTO notification (message, user_id) VALUES (?, ?)",
                (message, user_id),
            )

        conn.commit()
        print("Database seeded successfully!")

        # Print summary
        cur.execute("SELECT COUNT(*) FROM student")
        student_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM book")
        book_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM rental")
        rental_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM notification")
        notification_count = cur.fetchone()[0]

        print(f"\nSummary:")
        print(f"- Students: {student_count}")
        print(f"- Books: {book_count}")
        print(f"- Rentals: {rental_count}")
        print(f"- Notifications: {notification_count}")

    except Exception as e:
        print(f"Error seeding database: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
