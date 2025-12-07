import sqlite3
from typing import Dict, Any
from datetime import datetime, timedelta

class Rental:
    def rent_book(self, conn: sqlite3.Connection, student_id: int, book_id: int) -> Dict[str, Any]:
        try:
            cur = conn.cursor()
            
            # 1. Check if student exists and is not suspended
            cur.execute("SELECT isSuspended FROM student WHERE id = ?", (student_id,))
            student = cur.fetchone()
            if not student:
                return {'status': False, 'message': 'Student not found.'}
            if student[0]: # isSuspended is True
                return {'status': False, 'message': 'Account is suspended. Cannot rent books.'}

            # 2. Check if book is available
            cur.execute("SELECT id FROM rental WHERE book_id = ? AND is_returned = 0", (book_id,))
            if cur.fetchone():
                return {'status': False, 'message': 'Book is currently rented out.'}

            # 3. Create Rental (7 days)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)
            
            # SQLite usually stores dates as strings in YYYY-MM-DD
            cur.execute("""
                INSERT INTO rental (student_id, book_id, rental_start, rental_end, is_returned)
                VALUES (?, ?, ?, ?, 0)
            """, (student_id, book_id, start_date.date(), end_date.date()))
            
            conn.commit()
            return {'status': True, 'message': 'Book rented successfully.', 'due_date': end_date.date()}
            
        except Exception as e:
            conn.rollback()
            return {'status': False, 'message': f'Error renting book: {str(e)}'}
    
    def get_student_rentals(self, conn: sqlite3.Connection, student_id: int) -> list:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.title, r.rental_end, r.rental_start
            FROM rental r
            JOIN book b ON r.book_id = b.id
            WHERE r.student_id = ? AND r.is_returned = 0
        """, (student_id,))
        rentals = cur.fetchall()
        
        my_rentals = []
        for r in rentals:
            my_rentals.append({
                'title': r[0],
                'due_date': r[1],
                'start_date': r[2]
            })
        return my_rentals
