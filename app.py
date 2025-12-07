from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session

# Import refactored models
from model.database import Database
from model.student import Student
from model.book import Book
from model.rental import Rental

from datetime import datetime

app = Flask(__name__)

# settings
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "cn382_your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# start flask session
sess = Session()
sess.init_app(app)

# Instantiate models
db = Database()
student_model = Student()
book_model = Book()
rental_model = Rental()

@app.context_processor
def inject_today():
    return {'today': datetime.now().date()}

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
        
        conn = db.connect()
        result = student_model.create_account(conn, name, email, password)
        conn.close()
        
        if result['status']:
            flash("Account created! Please log in.", "success")
            return redirect(url_for('student_login'))
        else:
            flash(result['message'], "danger")
            
    return render_template("student_register.html")

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        conn = db.connect()
        result = student_model.login(conn, {'email': email, 'password': password})
        conn.close()
        
        if result['status']:
            user_data = result['data']
            session["user_id"] = user_data['id']
            session["user_name"] = user_data['name']
            session["is_suspended"] = user_data['isSuspended']
            return redirect(url_for('student_dashboard'))
        else:
            flash(result['message'], "danger")
            
    return render_template("student_login.html")

@app.route("/student/logout")
def student_logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/student/dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect(url_for('student_login'))
    
    user_id = session["user_id"]
    conn = db.connect()
    
    # Refresh suspension status
    # We can peek at key in student login or just query it simply
    # Reuse check_notifications which updates it if needed
    
    # Get Notifications
    notifications = student_model.check_notifications(conn, user_id)
    
    # Re-fetch suspension status after check_notifications might have updated it
    cur = conn.cursor()
    cur.execute("SELECT isSuspended FROM student WHERE id = ?", (user_id,))
    res = cur.fetchone()
    if res:
        session["is_suspended"] = res[0]

    # Get Current Rentals
    my_rentals = rental_model.get_student_rentals(conn, user_id)
    
    conn.close()

    return render_template("student_dashboard.html", 
                           user_name=session["user_name"], 
                           notifications=notifications,
                           rentals=my_rentals,
                           is_suspended=session.get("is_suspended"))

@app.route("/student/books", methods=["GET"])
def student_books():
    if "user_id" not in session:
        return redirect(url_for('student_login'))
        
    query = request.args.get("q", "")
    conn = db.connect()
    books = book_model.search_available(conn, query)
    conn.close()
    
    return render_template("student_books.html", books=books, search_query=query)

@app.route("/student/rent/<int:book_id>", methods=["POST"])
def rent_book_route(book_id):
    if "user_id" not in session:
        return jsonify({'status': False, 'message': 'Not logged in'})
        
    user_id = session["user_id"]
    conn = db.connect()
    result = rental_model.rent_book(conn, user_id, book_id)
    conn.close()
    
    return jsonify(result)

@app.route("/student/delete_account", methods=["POST"])
def delete_my_account():
    if "user_id" not in session:
        return redirect(url_for('student_login'))
    
    conn = db.connect()
    result = student_model.delete_account(conn, session["user_id"])
    conn.close()
    
    if result['status']:
        session.clear()
        flash("Account deleted.", "info")
        return redirect(url_for('home'))
    else:
        flash(result['message'], "danger")
        return redirect(url_for('student_dashboard'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
