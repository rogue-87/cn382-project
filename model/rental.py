import sqlite3
from typing import Dict, Any, List
from datetime import datetime, timedelta
from lib.response import Response, Status


class Rental:
    def rent_book(
        self, connection: sqlite3.Connection, student_id: int, book_id: int
    ) -> Response:
        try:
            cursor = connection.cursor()

            # 1. Check if student exists and is not suspended
            cursor.execute(
                "SELECT isSuspended FROM student WHERE id = ?", (student_id,)
            )
            student = cursor.fetchone()
            if not student:
                return Response(Status.FAIL, "Student not found.")
            if student[0]:  # isSuspended is True
                return Response(Status.FAIL, "Account is suspended. Cannot rent books.")

            # 2. Check if book is available
            cursor.execute(
                "SELECT id FROM rental WHERE book_id = ? AND is_returned = 0",
                (book_id,),
            )
            if cursor.fetchone():
                return Response(Status.FAIL, "Book is currently rented out.")

            # 3. Create Rental (7 days)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)

            # SQLite usually stores dates as strings in YYYY-MM-DD
            cursor.execute(
                """
                INSERT INTO rental (student_id, book_id, rental_start, rental_end, is_returned)
                VALUES (?, ?, ?, ?, 0)
            """,
                (student_id, book_id, start_date.date(), end_date.date()),
            )

            connection.commit()
            return Response(
                Status.SUCCESS, "Book rented successfully.", end_date.date()
            )

        except Exception as e:
            connection.rollback()
            return Response(Status.FAIL, f"Error renting book: {str(e)}")

    def get_student_rentals(
        self, connection: sqlite3.Connection, student_id: int
    ) -> list:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT b.title, r.rental_end, r.rental_start
            FROM rental r
            JOIN book b ON r.book_id = b.id
            WHERE r.student_id = ? AND r.is_returned = 0
        """,
            (student_id,),
        )
        rentals = cursor.fetchall()

        my_rentals = []
        for r in rentals:
            my_rentals.append(
                {
                    "title": r[0],
                    "due_date": datetime.strptime(r[1], "%Y-%m-%d").date(),
                    "start_date": datetime.strptime(r[2], "%Y-%m-%d").date(),
                }
            )
        return my_rentals

    def get_all_rentals(self, connection: sqlite3.Connection) -> List[Dict[str, Any]]:
        """
        Get all rentals with student and book info.
        """
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT r.id, s.name, b.title, r.rental_start, r.rental_end, r.is_returned
                FROM rental r
                JOIN student s ON r.student_id = s.id
                JOIN book b ON r.book_id = b.id
                ORDER BY r.rental_start DESC
            """)
            rows = cursor.fetchall()

            rentals = []
            for row in rows:
                rentals.append(
                    {
                        "id": row[0],
                        "student_name": row[1],
                        "book_title": row[2],
                        "rental_start": row[3],
                        "rental_end": row[4],
                        "is_returned": row[5],
                    }
                )
            return rentals
        except Exception:
            return []

    def return_book(self, connection: sqlite3.Connection, rental_id: int) -> Response:
        """
        Mark a rental as returned.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE rental SET is_returned = 1 WHERE id = ?", (rental_id,)
            )
            if cursor.rowcount == 0:
                return Response(Status.FAIL, "Rental not found.")
            connection.commit()
            return Response(Status.SUCCESS, "Book returned successfully.")
        except Exception as e:
            return Response(Status.FAIL, f"Error returning book: {str(e)}")
