from flask import Flask, render_template, request
from groq import Groq
import os

app = Flask(__name__)

# Ensure you have set the GROQ_API_KEY in your environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY")) 

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

## Route to handle the prediction logic for basic prediction
@app.route("/prediction", methods=["POST"])
def prediction():
    q = float(request.form.get("q"))
    prediction_result = (-50.6 * q) + 90.2
    return render_template("prediction.html", r=prediction_result)


## Route to handle the prediction logic using Groq API
# @app.route("/prediction", methods=["POST"])
# def prediction():
#     q = request.form.get("q")
#     prompt = f"What is the expected DBS share price if the USD/SGD exchange rate is {q}?"

#     completion = client.chat.completions.create(
#         model="llama3-8b-8192",  # or try "mixtral-8x7b-32768"
#         messages=[{"role": "user", "content": prompt}]
#     )
#     reply = completion.choices[0].message.content
#     return render_template("prediction.html", r=reply)

if __name__ == "__main__":
    app.run(debug=True)