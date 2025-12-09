import sqlite3
from typing import List, Dict, Any, Optional

from lib.response import Response, Status


class Book:
    def search_available(
        self, connection: sqlite3.Connection, query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search for books by title or author.
        Only returns books that are not currently rented out.
        """
        try:
            cursor = connection.cursor()
            sql_query = """
                SELECT b.id, b.title, b.author, b.description, b.publishDate, b.isbn, b.quantity
                FROM book b
                WHERE (b.title LIKE ? OR b.author LIKE ?)
                AND b.id NOT IN (
                    SELECT book_id FROM rental WHERE is_returned = 0
                )
            """
            search_term = f"%{query}%"
            cursor.execute(sql_query, (search_term, search_term))
            rows = cursor.fetchall()

            books = []
            for row in rows:
                books.append(
                    {
                        "id": row[0],
                        "title": row[1],
                        "author": row[2],
                        "description": row[3],
                        "publishDate": row[4],
                        "isbn": row[5],
                        "quantity": row[6],
                    }
                )
            return books
        except Exception:
            return []

    def get_all_books(self, connection: sqlite3.Connection) -> List[Dict[str, Any]]:
        """
        Get all books with available quantity.
        """
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT b.id, b.title, b.author, b.description, b.publishDate, b.isbn, b.quantity,
                       b.quantity - COALESCE(r.rented_count, 0) as available_quantity
                FROM book b
                LEFT JOIN (
                    SELECT book_id, COUNT(*) as rented_count
                    FROM rental
                    WHERE is_returned = 0
                    GROUP BY book_id
                ) r ON b.id = r.book_id
            """)
            rows = cursor.fetchall()

            books = []
            for row in rows:
                books.append(
                    {
                        "id": row[0],
                        "title": row[1],
                        "author": row[2],
                        "description": row[3],
                        "publishDate": row[4],
                        "isbn": row[5],
                        "quantity": row[6],
                        "available_quantity": row[7],
                    }
                )
            return books
        except Exception:
            return []

    def add_book(
        self,
        connection: sqlite3.Connection,
        title: str,
        author: str,
        isbn: str,
        quantity: int,
    ) -> Response:
        """
        Add a new book.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO book (title, author, isbn, quantity) VALUES (?, ?, ?, ?)",
                (title, author, isbn, quantity),
            )
            connection.commit()
            return Response(Status.SUCCESS, "Book added successfully.")
        except Exception as e:
            return Response(Status.FAIL, f"Error adding book: {str(e)}")

    def update_book(
        self,
        connection: sqlite3.Connection,
        book_id: int,
        title: str,
        author: str,
        isbn: str,
        quantity: int,
    ) -> Response:
        """
        Update an existing book.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE book SET title = ?, author = ?, isbn = ?, quantity = ? WHERE id = ?",
                (title, author, isbn, quantity, book_id),
            )
            if cursor.rowcount == 0:
                return Response(Status.FAIL, "Book not found.")
            connection.commit()
            return Response(Status.SUCCESS, "Book updated successfully.")
        except Exception as e:
            return Response(Status.SUCCESS, f"Error updating book: {str(e)}")

    def delete_book(self, connection: sqlite3.Connection, book_id: int) -> Response:
        """
        Delete a book.
        """
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
            if cursor.rowcount == 0:
                return Response(Status.FAIL, "Book not found.")
            connection.commit()
            return Response(Status.SUCCESS, "Book deleted successfully.")

        except Exception as e:
            return Response(Status.FAIL, f"Error deleting book: {str(e)}")

    def get_book_by_id(
        self, connection: sqlite3.Connection, book_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a book by ID.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, title, author, description, publishDate, isbn, quantity FROM book WHERE id = ?",
                (book_id,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "author": row[2],
                    "description": row[3],
                    "publishDate": row[4],
                    "isbn": row[5],
                    "quantity": row[6],
                }
            return None
        except Exception:
            return None
