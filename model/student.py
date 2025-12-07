import sqlite3
from typing import Dict, Any, List
from datetime import datetime, timedelta

class Student:
    def create_account(self, conn: sqlite3.Connection, name: str, email: str, password: str = "1234") -> Dict[str, Any]:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO student (name, email, password, isSuspended) VALUES (?, ?, ?, ?)", (name, email, password, False))
            conn.commit()
            return {'status': True, 'message': 'Student account created successfully.'}
        except sqlite3.IntegrityError:
            return {'status': False, 'message': 'Email already exists.'}
        except Exception as e:
            return {'status': False, 'message': f'Error creating account: {str(e)}'}

    def login(self, conn: sqlite3.Connection, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Authenticates a student using email and password.
        Expected data: {'email': '...', 'password': '...'}
        """
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, password, isSuspended FROM student WHERE email = ? AND password = ?", 
                        (data['email'], data['password']))
            user = cur.fetchone()
            
            if user:
                user_dict = {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'isSuspended': user[4]
                }
                return {'status': True, 'data': user_dict}
            else:
                return {'status': False, 'message': 'Invalid email or password.'}
                
        except Exception as e:
            return {'status': False, 'message': f'Authentication error: {str(e)}'}

    def delete_account(self, conn: sqlite3.Connection, student_id: int) -> Dict[str, Any]:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM student WHERE id = ?", (student_id,))
            if cur.rowcount == 0:
                 return {'status': False, 'message': 'Student not found.'}
            conn.commit()
            return {'status': True, 'message': 'Student account deleted successfully.'}
        except Exception as e:
            return {'status': False, 'message': f'Error deleting account: {str(e)}'}

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
