from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/prediction", methods=["POST"])
def prediction():
    q = float(request.form.get("q"))
    prediction_result = (-50.6 * q) + 90.2
    return render_template("prediction.html", r=prediction_result)

if __name__ == "__main__":
    app.run(debug=True)