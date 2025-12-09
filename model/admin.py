from model.database import Database
from model.book import Book
from model.student import Student
from model.rental import Rental


class Admin:
    def __init__(self):
        self.db = Database()
        self.book_model = Book()
        self.student_model = Student()
        self.rental_model = Rental()

    # --- Book Management ---
    def get_all_books(self):
        connection = self.db.connect()
        books = self.book_model.get_all_books(connection)
        connection.close()
        return books

    def add_book(self, title, author, isbn, quantity):
        connection = self.db.connect()
        result = self.book_model.add_book(connection, title, author, isbn, quantity)
        connection.close()
        return result

    def update_book(self, book_id, title, author, isbn, quantity):
        connection = self.db.connect()
        result = self.book_model.update_book(
            connection, book_id, title, author, isbn, quantity
        )
        connection.close()
        return result

    def delete_book(self, book_id):
        connection = self.db.connect()
        result = self.book_model.delete_book(connection, book_id)
        connection.close()
        return result

    def get_book_by_id(self, book_id):
        connection = self.db.connect()
        book = self.book_model.get_book_by_id(connection, book_id)
        connection.close()
        return book

    # NOTE: Student Management
    def get_all_students(self):
        connection = self.db.connect()
        students = self.student_model.get_all_students(connection)
        connection.close()
        return students

    def get_student_by_id(self, student_id):
        connection = self.db.connect()
        student = self.student_model.get_student_by_id(connection, student_id)
        connection.close()
        return student

    def update_student_suspension(self, student_id, is_suspended):
        connection = self.db.connect()
        result = self.student_model.update_suspension_status(
            connection, student_id, is_suspended
        )
        connection.close()
        return result

    def delete_student(self, student_id):
        connection = self.db.connect()
        result = self.student_model.delete_account(connection, student_id)
        connection.close()
        return result

    def search_students(self, query="", sort_by="id", sort_order="ASC"):
        connection = self.db.connect()
        students = self.student_model.search_students(
            connection, query, sort_by, sort_order
        )
        connection.close()
        return students

    def update_student(self, student_id, name=None, password=None):
        connection = self.db.connect()
        result = self.student_model.update_student(
            connection, student_id, name, password
        )
        connection.close()
        return result

    # NOTE: Rental Management
    def get_all_rentals(self):
        connection = self.db.connect()
        rentals = self.rental_model.get_all_rentals(connection)
        connection.close()
        return rentals

    def return_book(self, rental_id):
        connection = self.db.connect()
        result = self.rental_model.return_book(connection, rental_id)
        connection.close()
        return result

    # NOTE: Notification Management
    def get_all_notifications(self):
        connection = self.db.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM notification")
        notifications = cursor.fetchall()
        connection.close()
        return notifications

    def add_notification(self, message, user_id=None):
        connection = self.db.connect()
        cursor = connection.cursor()
        if user_id:
            cursor.execute(
                "INSERT INTO notification (message, user_id) VALUES (?, ?)",
                (message, user_id),
            )
        else:
            cursor.execute("INSERT INTO notification (message) VALUES (?)", (message,))
        connection.commit()
        connection.close()
        return {"status": True, "message": "Notification added."}

    def delete_notification(self, notification_id):
        connection = self.db.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM notification WHERE id = ?", (notification_id,))
        connection.commit()
        connection.close()
        return {"status": True, "message": "Notification deleted."}
