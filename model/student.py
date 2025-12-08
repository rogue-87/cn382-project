import sqlite3
from typing import Dict, Any, List
from datetime import datetime, timedelta
from model.database import Database

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

    ## remove login

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


