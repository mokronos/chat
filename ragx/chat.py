import flask
from flask import render_template, make_response
import requests

app = flask.Flask(__name__)

@app.route('/')
def index():
    return render_template('chat/index.html')

class Chat:
    def __init__(self):
        self.messages = []

    def add_message(self, message, role="user"):
        self.messages.append({"role": role, "content": message})

    def clear(self):
        self.messages.clear()

    def __iter__(self):
        return iter(self.messages)

messages = Chat()
@app.route('/chat', methods=['GET', 'POST', 'DELETE'])
def chat():
    match flask.request.method:
        case 'DELETE':
            messages.clear()
            return render_template('chat/mess.html', messages=messages)
        case 'POST':
            message = flask.request.form['message']
            messages.add_message(message)
            response = make_response(render_template('chat/mess.html', messages=messages))
            response.headers['HX-Trigger'] = 'getModelResponse'
            return response
        case _:
            return render_template('chat/chat.html', messages=messages)

@app.route('/model_response', methods=['GET'])
def model_response():
    match flask.request.method:
        case 'GET':
            call_model()
            return render_template('chat/mess.html', messages=messages)
        case _:
            return render_template('chat/chat.html', messages=messages)

def call_model(model: str="llama3:8b") -> str:

    if model=="llama3:8b":

        url = "http://localhost:11434/api/chat"

        payload = {
            "model": model,
            "messages": messages.messages,
            "stream": False
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            resp = response.json()
            messages.add_message(resp["message"]["content"], resp["message"]["role"])
            return "Model found"


    
    return "Model not found"
