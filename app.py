from flask import Flask, render_template, request
import os

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

## Route to handle the DBS prediction page
@app.route("/dbs", methods=["GET","POST"])
def dbs():
    return render_template("dbs.html")

## Route to handle the prediction logic for basic prediction
@app.route("/prediction", methods=["POST"])
def prediction():
    q = float(request.form.get("q"))
    prediction_result = (-50.6 * q) + 90.2
    return render_template("prediction.html", r=prediction_result)

if __name__ == "__main__":
    app.run(debug=True)