from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_session import Session
from dotenv import load_dotenv
from functools import wraps
import os

# Import refactored models
from model.database import Database
from model.student import Student
from model.authentication import Authentication
from model.book import Book
from model.rental import Rental
from model.notification import Notification
from model.admin import Admin

from datetime import datetime

app = Flask(__name__)

# settings
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# start flask session
sess = Session()
sess.init_app(app)

# Instantiate models
db = Database()
student_model = Student()
auth_model = Authentication()
book_model = Book()
rental_model = Rental()
notification_model = Notification()
admin_model = Admin()


@app.context_processor
def inject_today():
    return {"today": datetime.now().date()}


@app.route("/")
def home():
    return render_template("index.html")


# --- Student Routes ---
@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        ##conn = db.connect()
        result = student_model.create_account(
            Database().connect(), name, email, password
        )
        ##conn.close()

        if result["status"]:
            flash("Account created! Please log in.", "success")
            return redirect(url_for("student_login"))
        else:
            flash(result["message"], "danger")

    return render_template("student/register.html")


@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        result = auth_model.login(
            Database().connect(), {"email": email, "password": password}
        )

        if result["status"]:
            user_data = result["data"]
            session["user_id"] = user_data["id"]
            session["user_name"] = user_data["name"]
            session["is_suspended"] = user_data["isSuspended"]
            return redirect(url_for("student_dashboard"))
        else:
            flash(result["message"], "danger")

    return render_template("student/login.html")


@app.route("/student/logout")
def student_logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/student/dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    ##conn = db.connect()

    # Refresh suspension status
    # We can peek at key in student login or just query it simply
    # Reuse check_notifications which updates it if needed

    # Get Notifications
    notifications = notification_model.check_notifications(
        Database().connect(), user_id
    )

    # Re-fetch suspension status after check_notifications might have updated it
    connection = Database().connect()
    cursor = connection.cursor()
    cursor.execute("SELECT isSuspended FROM student WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    if res:
        session["is_suspended"] = res[0]
    connection.close()

    # Get Current Rentals
    my_rentals = rental_model.get_student_rentals(Database().connect(), user_id)

    ##conn.close()
    Database().connect().close()  ## optional just to test

    return render_template(
        "student/dashboard.html",
        user_name=session["user_name"],
        notifications=notifications,
        rentals=my_rentals,
        is_suspended=session.get("is_suspended"),
    )


@app.route("/student/books", methods=["GET"])
def student_books():
    if "user_id" not in session:
        return redirect(url_for("login"))

    query = request.args.get("q", "")
    ##conn = db.connect()
    books = book_model.search_available(Database().connect(), query)
    ##conn.close()

    return render_template("student/books.html", books=books, search_query=query)


@app.route("/student/rent/<int:book_id>", methods=["POST"])
def rent_book_route(book_id):
    if "user_id" not in session:
        return jsonify({"status": False, "message": "Not logged in"})

    user_id = session["user_id"]
    ##conn = db.connect()
    result = rental_model.rent_book(Database().connect(), user_id, book_id)
    ##conn.close()

    return jsonify(result)


@app.route("/student/delete_account", methods=["POST"])
def delete_my_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # conn = db.connect()
    result = student_model.delete_account(Database().connect(), session["user_id"])
    # conn.close()

    if result["status"]:
        session.clear()
        flash("Account deleted.", "info")
        return redirect(url_for("home"))
    else:
        flash(result["message"], "danger")
        return redirect(url_for("student/dashboard.html"))


# --- Admin Routes ---
load_dotenv()
ADMIN_NAME = str(os.getenv("ADMIN_NAME"))
ADMIN_PASSWORD = str(os.getenv("ADMIN_PASSWORD"))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "is_admin" not in session or not session["is_admin"]:
            flash("Admin access required.", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_NAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Logged in as Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("admin/login.html")


@app.route("/admin/logout")
@admin_required
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out as Admin.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html")


# --- Admin Book Management Routes ---
@app.route("/admin/books")
@admin_required
def admin_books():
    books = admin_model.get_all_books()
    return render_template(
        "admin/book_list.html", books=books
    )  # Changed template to book_list.html


@app.route("/admin/books/add", methods=["GET", "POST"])
@admin_required
def admin_add_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        isbn = request.form.get("isbn")
        quantity = int(request.form.get("quantity"))

        result = admin_model.add_book(title, author, isbn, quantity)
        if result["status"]:
            flash("Book added successfully!", "success")
            return redirect(url_for("admin_books"))
        else:
            flash(result["message"], "danger")

    return render_template("admin/book_form.html", book=None)


@app.route("/admin/books/edit/<int:book_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_book(book_id):
    book = admin_model.get_book_by_id(book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for("admin_books"))

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        isbn = request.form.get("isbn")
        quantity = int(request.form.get("quantity"))

        result = admin_model.update_book(book_id, title, author, isbn, quantity)
        if result["status"]:
            flash("Book updated successfully!", "success")
            return redirect(url_for("admin_books"))
        else:
            flash(result["message"], "danger")

    return render_template("admin/book_form.html", book=book)


@app.route("/admin/books/delete/<int:book_id>", methods=["POST"])
@admin_required
def admin_delete_book(book_id):
    result = admin_model.delete_book(book_id)
    if result["status"]:
        flash("Book deleted successfully!", "success")
    else:
        flash(result["message"], "danger")
    return redirect(url_for("admin_books"))


# --- Admin Student Management Routes ---
@app.route("/admin/students")
@admin_required
def admin_students():
    query = request.args.get("q", "")
    sort_by = request.args.get("sort_by", "id")
    sort_order = request.args.get("sort_order", "ASC")
    students = admin_model.search_students(query, sort_by, sort_order)
    return render_template("admin/student_list.html", students=students)


@app.route("/admin/students/edit/<int:student_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_student(student_id):
    student = admin_model.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("admin_students"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        result = admin_model.update_student(student_id, name, password)
        if result["status"]:
            flash("Student updated successfully!", "success")
            return redirect(url_for("admin_students"))
        else:
            flash(result["message"], "danger")

    return render_template("admin/student_form.html", student=student)


@app.route("/admin/students/suspend/<int:student_id>", methods=["POST"])
@admin_required
def admin_suspend_student(student_id):
    suspend = request.form.get("suspend") == "1"
    result = admin_model.update_student_suspension(student_id, suspend)
    if result["status"]:
        status = "suspended" if suspend else "unsuspended"
        flash(f"Student {status} successfully!", "success")
    else:
        flash(result["message"], "danger")
    return redirect(url_for("admin_students"))


@app.route("/admin/students/delete/<int:student_id>", methods=["POST"])
@admin_required
def admin_delete_student(student_id):
    result = admin_model.delete_student(student_id)
    if result["status"]:
        flash("Student deleted successfully!", "success")
    else:
        flash(result["message"], "danger")
    return redirect(url_for("admin_students"))


# --- Admin Rental Management Routes ---
@app.route("/admin/rentals")
@admin_required
def admin_rentals():
    rentals = admin_model.get_all_rentals()
    return render_template("admin/rental_list.html", rentals=rentals)


@app.route("/admin/rentals/return/<int:rental_id>", methods=["POST"])
@admin_required
def admin_return_book(rental_id):
    result = admin_model.return_book(rental_id)
    if result["status"]:
        flash("Book returned successfully!", "success")
    else:
        flash(result["message"], "danger")
    return redirect(url_for("admin_rentals"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
