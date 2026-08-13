from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random, smtplib

app = Flask(__name__)
app.secret_key = "supersecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome {session['user']}!"
    return redirect(url_for('login'))

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        otp = random.randint(100000,999999)
        session['otp'] = otp
        session['reset_email'] = email
        # Normally send OTP via SMTP/email service
        print(f"OTP for {email}: {otp}")  # Debug only
        flash("OTP sent to your email!", "info")
        return redirect(url_for('verify_otp'))
    return render_template('forgot.html')

@app.route('/verify_otp', methods=['GET','POST'])
def verify_otp():
    if request.method == 'POST':
        entered = request.form['otp']
        if int(entered) == session['otp']:
            flash("OTP verified! Reset your password.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP", "danger")
    return render_template('verify.html')

@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if request.method == 'POST':
        new_pass = generate_password_hash(request.form['password'])
        user = User.query.filter_by(email=session['reset_email']).first()
        user.password = new_pass
        db.session.commit()
        flash("Password reset successful!", "success")
        return redirect(url_for('login'))
    return render_template('reset.html')

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
