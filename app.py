from flask import Flask, render_template
from flask_session import Session

app = Flask(__name__)

# settings
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "cn382_your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# start flask session
session = Session()
session.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
