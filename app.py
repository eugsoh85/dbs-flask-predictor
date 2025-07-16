from flask import Flask, render_template, request
from groq import Groq
import joblib
import os
import requests

# os.environ['GROQ_API_KEY'] = "gs......."
# For cloud deployment, ensure the GROQ_API_KEY is set in the environment variables

# Only load .env in development (not needed in production)
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

## Route to handle the main page logic
@app.route("/main", methods=["GET","POST"])
def main():
    q = request.form.get("q")
    # db
    return render_template("main.html")

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
    
    return render_template("telegram.html")


if __name__ == "__main__":
    app.run(debug=True)