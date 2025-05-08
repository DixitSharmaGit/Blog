import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)

# Correct database path using absolute path
db_path = os.path.join(os.getcwd(), "instance", "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)

# Admin credentials (can be moved to database later)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        comment_text = request.form["comment"]
        new_comment = Comment(post_id=0, name=name, comment_text=comment_text)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("home"))

    comments = (
        Comment.query.filter_by(post_id=0)
        .order_by(Comment.timestamp.desc())
        .all()
    )
    return render_template("index.html", comments=comments)


@app.route("/delete-comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    if not session.get("admin"):
        return "Unauthorized", 403
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


@app.route("/post/1")
def post1():
    return render_template("post1.html")


@app.route("/post/2")
def post2():
    return render_template("post2.html")


@app.route("/post/3")
def post3():
    return render_template("post3.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
