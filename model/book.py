import sqlite3
from typing import List, Dict, Any

class Book:
    def search_available(self, conn: sqlite3.Connection, query: str = "") -> List[Dict[str, Any]]:
        """
        Search for books by title or author.
        Only returns books that are not currently rented out.
        """
        try:
            cur = conn.cursor()
            sql_query = """
                SELECT b.id, b.title, b.author, b.description 
                FROM book b
                WHERE (b.title LIKE ? OR b.author LIKE ?)
                AND b.id NOT IN (
                    SELECT book_id FROM rental WHERE is_returned = 0
                )
            """
            search_term = f"%{query}%"
            cur.execute(sql_query, (search_term, search_term))
            rows = cur.fetchall()
            
            books = []
            for row in rows:
                books.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'description': row[3]
                })
            return books
        except Exception:
            return []
