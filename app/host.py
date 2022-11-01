from flask import Flask, request, make_response
from model.node import Node
import logging
import base64
import json
import os

SECRET = "SECRET"
FILES_PATH = "FILES_PATH"

GET = "GET"
POST = "POST"

app = Flask(__name__, static_url_path="")
log = app.logger

node = Node(os.environ.get(SECRET), os.environ.get(FILES_PATH), log)

@app.route('/pub-key-list', methods=[GET])
def pub_key_list():
    message, status = node.get_pub_key_list()
    return make_response(message, status)

@app.route('/connect', methods=[POST])
def connect():
    message, status = node.connect(request.json)
    return make_response(message, status)

@app.route('/join', methods=[POST])
def join():
    message, status = node.join_node(request.json)
    return make_response(message, status)

@app.route('/update', methods=[POST])
def update():
    message, status = node.update_node(request.json)
    return make_response(message, status)

@app.route('/send-message-to-verification', methods=[POST])
def send_message():
    message, status = node.send_message_to_verification(request.json)
    return make_response(message, status)

@app.route('/verify-message-from-node', methods=[POST])
def receive_message():
    message, status = node.verify_message_from_node(request.json)
    return make_response(message, status)