from flask import Flask, render_template, request
from groq import Groq
import joblib
import os

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

if __name__ == "__main__":
    app.run(debug=True)