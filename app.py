from flask import Flask
from markupsafe import escape

app = Flask(__name__)

@app.route("/about")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/about")
def about():
    return "<p>This is the about page.</p>"

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!\n"