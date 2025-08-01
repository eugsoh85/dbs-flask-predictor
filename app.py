from flask import Flask, render_template, request
from groq import Groq
import joblib
import os
import requests

import sqlite3
from flask import g
import datetime
from datetime import datetime

# os.environ['GROQ_API_KEY'] = "gs......."
# For cloud deployment, ensure the GROQ_API_KEY is set in the environment variables

# Only load .env in development (not needed in production)
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

## Route to handle the main page logic
@app.route("/main", methods=["GET","POST"])
def main():
    q = request.form.get("q")
    # db
    if q:  # only log if a name was submitted
        import sqlite3
        import datetime
        t = datetime.datetime.now()

        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute('INSERT INTO user (name, timestamp) VALUES (?, ?)', (q, t))
        conn.commit()
        c.close()
        conn.close()
    
    return render_template("main.html")

## Route to handle the user logs page
@app.route("/users", methods=["POST"])
def users():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('SELECT name, timestamp FROM user')
    raw_logs = c.fetchall()
    c.close()
    conn.close()

    if not raw_logs:  # Check if logs are empty
        return render_template("users.html", message="No logs to display.")
    
    # Format timestamps
    logs = [
        (name, datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime("%d %b %Y, %I:%M %p"))
        for name, timestamp in raw_logs
    ]
    
    return render_template("users.html", logs=logs)

## Route to handle the deletion of user logs
@app.route("/delete_log", methods=["POST"])
def delete_log():
    import sqlite3

    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('DELETE FROM user')  # delete all rows from user table
    conn.commit()
    c.close()
    conn.close()

    return render_template("users_delete.html")

## Route to handle the HF Sepia Transformer page
@app.route('/sepia', methods=['GET', 'POST'])
def sepia():
    return render_template("hf_sepia.html")


## Route to handle the LLAMA chatbot page
@app.route("/llama", methods=["GET","POST"])
def llama():
    return render_template("llama.html")

## Route to handle the DeepSeek chatbot page
@app.route("/deepseek", methods=["GET","POST"])
def deepseek():
    return render_template("deepseek.html")

## Route to handle the LLAMA chatbot reply logic
@app.route("/llama_reply", methods=["POST"])
def llama_reply():
    q = request.form.get("q")
    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    return (render_template("llama_reply.html", r=completion.choices[0].message.content))

## Route to handle the DeepSeek chatbot reply logic
@app.route("/deepseek_reply", methods=["POST"])
def deepseek_reply():
    q = request.form.get("q")
    client = Groq()
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    return (render_template("deepseek_reply.html", r=completion.choices[0].message.content))

## Route to handle the DBS prediction page
@app.route("/dbs", methods=["GET","POST"])
def dbs():
    return render_template("dbs.html")

## Route to handle the prediction logic for basic prediction
@app.route("/prediction", methods=["POST"])
def prediction():
    q = float(request.form.get("q"))
    
     # load model
    model = joblib.load("dbs.jl")
    # make prediction
    pred = model.predict([[q]])
    
    return(render_template("prediction.html", r=pred))

## Route to handle the Telegram chatbot page
@app.route("/telegram", methods=["GET","POST"])
def telegram():
    
    domain_url = 'https://dbs-flask-predictor.onrender.com'

    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    
    # Set the webhook URL for the Telegram bot
    set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={domain_url}/webhook"
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot is running. Please check with the telegram bot. @sctp_eugsoh_genAI_bot"
    else:
        status = "Failed to start the telegram bot. Please check the logs."
    
    return render_template("telegram.html", status=status)

@app.route("/webhook",methods=["GET","POST"])
def webhook():

    # This endpoint will be called by Telegram when a new message is received
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update["message"]["chat"]["id"]
        query = update["message"]["text"]

        # Pass the query to the Groq model
        client = Groq()
        completion_ds = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        response_message = completion_ds.choices[0].message.content

        # Send the response back to the Telegram chat
        send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_message_url, json={
        })
    return('ok', 200)

@app.route("/end_telegram", methods=["GET","POST"])
def end_telegram():
    domain_url = 'https://dbs-flask-predictor.onrender.com'

    # Delete the existing Telegram webhook
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    response = requests.post(delete_webhook_url, json={"drop_pending_updates": True})

    # Log the response (useful on Render logs)
    print("🛑 Webhook Deletion Response:", response.json())

    if response.status_code == 200 and response.json().get("ok"):
        status = "✅ Telegram bot session has ended. Webhook successfully deleted."
    else:
        status = "❌ Failed to stop the Telegram bot. Please check the logs."

    return render_template("telegram.html", status=status)

if __name__ == "__main__":
    app.run(debug=True)
      