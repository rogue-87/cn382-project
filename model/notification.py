import sqlite3
from typing import Dict, Any, List
from datetime import datetime, timedelta
from model.database import Database

class Notification:
    def check_notifications(self, conn: sqlite3.Connection, student_id: int) -> List[str]:
            """
            Checks for rental warnings and updates suspension status if overdue.
            Returns a list of notification messages.
            """
            notifications = []
            try:
                cur = conn.cursor()
                
                # Get active rentals for student
                cur.execute("""
                    SELECT r.id, r.rental_end, b.title 
                    FROM rental r
                    JOIN book b ON r.book_id = b.id
                    WHERE r.student_id = ? AND r.is_returned = 0
                """, (student_id,))
                rentals = cur.fetchall()
                
                today = datetime.now().date()
                should_suspend = False
                
                for rental in rentals:
                    rental_end_str = rental[1]
                    book_title = rental[2]
                    
                    if isinstance(rental_end_str, str):
                        rental_end_date = datetime.strptime(rental_end_str, '%Y-%m-%d').date()
                    else:
                        rental_end_date = rental_end_str 
                    
                    # Check for overdue (Account Suspension)
                    if today > rental_end_date:
                        notifications.append(f"OVERDUE: Book '{book_title}' was due on {rental_end_date}. Account Suspended.")
                        should_suspend = True
                    
                    # Check for warning (3 days before)
                    elif today >= (rental_end_date - timedelta(days=3)):
                        days_left = (rental_end_date - today).days
                        notifications.append(f"WARNING: Book '{book_title}' is due in {days_left} days ({rental_end_date}).")
                        
                if should_suspend:
                    cur.execute("UPDATE student SET isSuspended = 1 WHERE id = ?", (student_id,))
                    conn.commit()
                    
                return notifications

            except Exception as e:
                return [f"Error checking notifications: {str(e)}"]
