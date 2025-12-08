import sqlite3
from typing import Dict, Any
from werkzeug.security import check_password_hash


class Authentication:
    def login(self, connection: sqlite3.Connection, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Authenticates a student using email and password.
        Expected data: {'email': '...', 'password': '...'}
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, name, email, password, isSuspended FROM student WHERE email = ?",
                (data["email"],),
            )
            user = cursor.fetchone()

            if user and check_password_hash(user[3], data["password"]):
                user_dict = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "isSuspended": user[4],
                }
                return {"status": True, "data": user_dict}
            else:
                return {"status": False, "message": "Invalid email or password."}

        except Exception as e:
            return {"status": False, "message": f"Authentication error: {str(e)}"}
