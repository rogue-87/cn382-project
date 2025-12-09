import sqlite3
from typing import Dict
from werkzeug.security import check_password_hash
from lib.response import Response, Status


class Authentication:
    def login(self, connection: sqlite3.Connection, data: Dict[str, str]) -> Response:
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
                return Response(
                    Status.SUCCESS, "Successfully authenticated!", user_dict
                )
            else:
                return Response(Status.FAIL, "Invalid email or password.")

        except Exception as e:
            return Response(Status.FAIL, f"Authentication error: {str(e)}")
