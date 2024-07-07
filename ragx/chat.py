import flask
from flask import render_template, make_response, stream_with_context, g
from flask.wrappers import Response
import requests
import time
from collections import defaultdict

app = flask.Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"


@app.route('/')
def index():
    return render_template('chat/index.html', data=[f"Hello World {i}" for i in range(20)])

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
            return render_template('chat/chat.html', messages=messages, chat_hash=hash(time.time()))

@app.route('/model_response', methods=['GET'])
def model_response():
    match flask.request.method:
        case 'GET':
            call_model()
            return "data: test"
        case _:
            return render_template('chat/chat.html', messages=messages)

queries = []
chats = defaultdict(dict)

@app.route('/chat_sse/<chat_hash>', methods=['GET'])
def chat_sse(chat_hash):

    message = f"I am reponding to your query {chats[chat_hash]["history"][-1]}"
    def generate():
        full_message = []
        for l in message:
            time.sleep(0.02)
            msg = f"event: message\ndata: {l}\n\n"
            full_message.append(l)
            yield msg
        msg = f"event: close\ndata: <p>closed</p>\n\n"
        chats[chat_hash]["history"][-1]["response"] = "".join(full_message)
        chats[chat_hash]["locked"] = False
        yield msg

    return Response(generate(), mimetype="text/event-stream")

@app.route('/query', methods=['POST'])
def query():
    print(chats)
    q = flask.request.form['query']
    chat_hash = flask.request.form['chat_hash']
    if chats[chat_hash].get("locked") is True:
        return Response("Chat is locked", status=400)
    chats[chat_hash]["locked"] = True
    if chats[chat_hash].get("history") is None:
        chats[chat_hash]["history"] = []
    chats[chat_hash]["history"].append({"query": q})
    print(chats[chat_hash]["history"])
    return render_template('chat/query.html', pairs=chats[chat_hash]["history"], chat_hash=chat_hash)

# def call_model(model: str="llama3:8b") -> str:
def call_model(model: str="phi3") -> str:

    if model in ["phi3", "llama3:8b"]:

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
