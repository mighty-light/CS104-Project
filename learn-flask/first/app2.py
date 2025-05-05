from flask import Flask
from markupsafe import escape
from markupsafe import Markup

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/user/<username>')
def show_user_profile(username):
    return f"User {escape(username)}"

@app.route('/post/<int:postid>')
def show_post(postid):
    return f"Post {postid}"

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    return f"Subpath {escape(subpath)}"

@app.route('/<name>')
def hello(name):
    return f"Hello, {escape(name)}"