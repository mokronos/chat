import flask
from flask import render_template

app = flask.Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

messages = []
@app.route('/chat', methods=['GET', 'POST', 'DELETE'])
def chat():
    match flask.request.method:
        case 'DELETE':
            messages.clear()
            return render_template('mess.html', messages=messages)
        case 'POST':
            message = flask.request.form['message']
            print(message)
            messages.append(message)
            return render_template('mess.html', messages=messages)
        case _:
            return render_template('chat.html', messages=messages)
