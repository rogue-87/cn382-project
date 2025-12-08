import sqlite3
from typing import Dict, Any, List
from datetime import datetime, timedelta
from model.database import Database

class Authentication:
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

