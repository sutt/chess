import flask

from flask import Flask
from flask import send_file
from flask import render_template
app = Flask(__name__)



@app.route('/demo_dynamic_url/<ij>')
def demo_dynamic_url(ij):
    fn = 'static/' + str(ij) + ".jpg"
    return str(ij)


@app.route('/')
def hello_world():
    return 'Hello, WSL!'


# export FLASK_APP=flask-server.py
# flask run [--host=0.0.0.0 (this enables outside access)]