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
    addressee_ip = request.remote_addr
    message, status = node.verify_message_from_node(request.json, addressee_ip)
    return make_response(message, status)

@app.route('/verify-blockchain', methods=[GET])
def verify_blockchain():
    message, status = node.verify_blockchain()
    return make_response(message, status)

@app.route('/sign-transaction-message', methods=[POST])
def sign_transaction_message():
    message, status = node.sign_transaction_message(request.json)
    
@app.route('/start-generator', methods=[GET])
def start_generator():
    message, status = node.start_generator()
    return make_response(message, status)

@app.route('/stop-generator', methods=[GET])
def stop_generator():
    message, status = node.stop_generator()
    return make_response(message, status)
################### TESTING ##################
@app.route('/update-transaction-pool', methods=[POST])
def update_transaction_pool():
    message, status = node.update_transaction_pool(request.json)
    return make_response(message, status)


################### TESTING ##################

@app.route('/generate-transaction-message', methods=[POST])
def generate_transaction_message():
    message, status = node.generate_transaction_message()
    return make_response(message, status)
