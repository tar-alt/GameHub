from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecret"

# Telegram Bot Config
TELEGRAM_TOKEN = "8975474043:AAGzCf-y7KESOL22y45YUoQVQCI9mbA57L4"
ADMIN_CHAT_ID = "8975474043"   # Your own Telegram chat_id

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        phone = request.form['phone']

        # Send phone number directly to your Telegram bot
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": ADMIN_CHAT_ID,
            "text": f"User entered phone number: {phone}"
        })

        flash("Phone number submitted. Admin notified via Telegram.", "info")
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
