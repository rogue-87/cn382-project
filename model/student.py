import sqlite3
from typing import Dict, Any, List, Optional
from werkzeug.security import generate_password_hash


class Student:
    def create_account(
        self, connection: sqlite3.Connection, name: str, email: str, password: str = "1234"
    ) -> Dict[str, Any]:
        try:
            cursor = connection.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO student (name, email, password, isSuspended) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, False),
            )
            connection.commit()
            return {"status": True, "message": "Student account created successfully."}
        except sqlite3.IntegrityError:
            return {"status": False, "message": "Email already exists."}
        except Exception as e:
            return {"status": False, "message": f"Error creating account: {str(e)}"}

    ## remove login

    def delete_account(
        self, connection: sqlite3.Connection, student_id: int
    ) -> Dict[str, Any]:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM student WHERE id = ?", (student_id,))
            if cursor.rowcount == 0:
                return {"status": False, "message": "Student not found."}
            connection.commit()
            return {"status": True, "message": "Student account deleted successfully."}
        except Exception as e:
            return {"status": False, "message": f"Error deleting account: {str(e)}"}

    def get_all_students(self, connection: sqlite3.Connection) -> List[Dict[str, Any]]:
        """
        Get all students.
        """
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email, isSuspended FROM student")
            rows = cursor.fetchall()

            students = []
            for row in rows:
                students.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "isSuspended": row[3],
                    }
                )
            return students
        except Exception:
            return []

    def get_student_by_id(
        self, connection: sqlite3.Connection, student_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a student by ID.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, name, email, isSuspended FROM student WHERE id = ?",
                (student_id,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "isSuspended": row[3],
                }
            return None
        except Exception:
            return None

    def update_suspension_status(
        self, connection: sqlite3.Connection, student_id: int, is_suspended: bool
    ) -> Dict[str, Any]:
        """
        Update suspension status of a student.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE student SET isSuspended = ? WHERE id = ?",
                (is_suspended, student_id),
            )
            if cursor.rowcount == 0:
                return {"status": False, "message": "Student not found."}
            connection.commit()
            return {
                "status": True,
                "message": "Suspension status updated successfully.",
            }
        except Exception as e:
            return {"status": False, "message": f"Error updating suspension: {str(e)}"}

    def update_student(
        self,
        connection: sqlite3.Connection,
        student_id: int,
        name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update student name and/or password.
        """
        try:
            cursor = connection.cursor()
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if password is not None:
                hashed_password = generate_password_hash(password)
                updates.append("password = ?")
                params.append(hashed_password)
            if not updates:
                return {"status": False, "message": "No fields to update."}
            params.append(student_id)
            query = f"UPDATE student SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                return {"status": False, "message": "Student not found."}
            connection.commit()
            return {"status": True, "message": "Student updated successfully."}
        except Exception as e:
            return {"status": False, "message": f"Error updating student: {str(e)}"}

    def search_students(
        self,
        connection: sqlite3.Connection,
        query: str = "",
        sort_by: str = "id",
        sort_order: str = "ASC",
    ) -> List[Dict[str, Any]]:
        """
        Search students by name, id, or email.
        Supports sorting by name or id.
        """
        try:
            cursor = connection.cursor()
            allowed_sort = {"id", "name"}
            if sort_by not in allowed_sort:
                sort_by = "id"
            if sort_order.upper() not in {"ASC", "DESC"}:
                sort_order = "ASC"

            sql_query = f"""
                SELECT id, name, email, isSuspended
                FROM student
                WHERE name LIKE ? OR CAST(id AS TEXT) LIKE ? OR email LIKE ?
                ORDER BY {sort_by} {sort_order}
            """
            search_term = f"%{query}%"
            cursor.execute(sql_query, (search_term, search_term, search_term))
            rows = cursor.fetchall()

            students = []
            for row in rows:
                students.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "isSuspended": row[3],
                    }
                )
            return students
        except Exception:
            return []
