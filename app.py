from flask import Flask, render_template, request, redirect, url_for, flash, session
import random, requests

app = Flask(__name__)
app.secret_key = "supersecret"

# Telegram Bot Config
TELEGRAM_TOKEN = "8975474043:AAGzCf-y7KESOL22y45YUoQVQCI9mbA57L4"
ADMIN_CHAT_ID = "8975474043"   # Admin (you)
USER_CHAT_ID = None            # Will be mapped per user

# Step 1: User enters phone number
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        phone = request.form['phone']
        session['pending_phone'] = phone

        # Notify admin
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": ADMIN_CHAT_ID,
            "text": f"User with phone {phone} requested login. Approve?"
        })

        flash("Admin has been notified. Please wait for approval.", "info")
        return redirect(url_for('request_otp'))
    return render_template('index.html')

# Step 2: Request OTP
@app.route('/request_otp')
def request_otp():
    otp = random.randint(100000,999999)
    session['otp'] = otp
    # Send OTP to user (for demo, send to admin chat)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={"chat_id": ADMIN_CHAT_ID, "text": f"OTP for {session['pending_phone']} is {otp}"})
    return render_template('verify.html')

# Step 3: Verify OTP
@app.route('/verify', methods=['POST'])
def verify():
    entered = request.form['otp']
    if int(entered) == session['otp']:
        flash("OTP correct. Waiting for admin approval.", "info")
        # Admin approval simulation
        session['approved'] = False
        return redirect(url_for('await_approval'))
    else:
        flash("Invalid OTP", "danger")
        return redirect(url_for('index'))

@app.route('/await_approval')
def await_approval():
    if session.get('approved'):
        session['user'] = session['pending_phone']
        return redirect(url_for('dashboard'))
    return "Waiting for admin approval..."

# Step 4: Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('index'))
