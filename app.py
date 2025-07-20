# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(50))
    type = db.Column(db.String(10))
    amount = db.Column(db.Float)
    note = db.Column(db.String(200))
    date = db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid username or password")
    return render_template("login.html", register=False)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registered successfully. Please login.")
            return redirect(url_for("login"))
    return render_template("login.html", register=True)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        category = request.form["category"]
        ttype = request.form["type"]
        amount = float(request.form["amount"])
        note = request.form["note"]
        date = datetime.now().strftime("%Y-%m-%d")
        exp = Expense(user_id=current_user.id, category=category, type=ttype, amount=amount, note=note, date=date)
        db.session.add(exp)
        db.session.commit()
        flash("Transaction added.")
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    income = sum(e.amount for e in expenses if e.type == 'Income')
    expense = sum(e.amount for e in expenses if e.type == 'Expense')
    return render_template("index.html", expenses=expenses, income=income, expense=expense)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
