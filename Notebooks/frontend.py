from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Wimbledon!"

@app.route("/next")
def next():
    return "Hello, Wimbledon Again!"


if __name__ == "__main__":
    app.run(debug=True)