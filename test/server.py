from flask import Flask, request, render_template
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import os

app = Flask(__name__)

@app.route('/')
def index():
    with open(os.path.dirname(__file__) + '/index.html', 'rb') as f:
        return f.read()


@app.route('/pipe')
def pipe():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']

        while True:
            ws.send(input())

if __name__ == "__main__":
    app.debug = True
    server = pywsgi.WSGIServer(("", 8080), app, handler_class=WebSocketHandler)
    server.serve_forever()
