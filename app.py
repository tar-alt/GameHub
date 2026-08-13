from flask import Flask, render_template, request, redirect, url_for, flash
import requests, sqlite3

app = Flask(__name__)
app.secret_key = "supersecret"

TELEGRAM_TOKEN = "8975474043:AAGzCf-y7KESOL22y45YUoQVQCI9mbA57L4"
ADMIN_CHAT_ID = "8975474043"

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (phone TEXT, chat_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- Webhook to capture chat_id ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', "")
        # For demo, assume user sends phone number to bot
        if text.isdigit():
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (phone, chat_id) VALUES (?, ?)", (text, chat_id))
            conn.commit()
            conn.close()
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          data={"chat_id": chat_id, "text": "Phone registered!"})
    return "ok"

# --- Web form ---
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        phone = request.form['phone']
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT chat_id FROM users WHERE phone=?", (phone,))
        row = c.fetchone()
        conn.close()

        if row:
            chat_id = row[0]
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          data={"chat_id": ADMIN_CHAT_ID, "text": f"User {phone} login request"})
            flash("Admin notified via Telegram.", "info")
        else:
            flash("Phone not registered with bot.", "danger")
        return redirect(url_for('index'))
    return render_template('index.html')
