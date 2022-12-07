from flask import Flask, request, make_response
from model.node import Node
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


@app.route('/save-candidate', methods=[POST])
def save_candidate():
    message, status = node.verify_and_save_candidate(request.json)
    return make_response(message, status)


@app.route('/start-generator', methods=[POST])
def start_generator():
    message, status = node.start_generator(request)
    return make_response(message, status)


@app.route('/stop-generator', methods=[POST])
def stop_generator():
    message, status = node.stop_generator()
    return make_response(message, status)


@app.route('/update-transaction-pool', methods=[POST])
def update_transaction_pool():
    message, status = node.update_transaction_pool(request.json)
    return make_response(message, status)


@app.route('/start-miner', methods=[POST])
def start_mining():
    message, status = node.start_miner()
    return make_response(message, status)


@app.route('/stop-miner', methods=[POST])
def stop_mining():
    message, status = node.stop_miner()
    return make_response(message, status)


@app.route('/current-balance', methods=[GET])
def get_current_balance():
    message, status = node.get_current_balance()
    return make_response(message, status)


@app.route('/get-block-count', methods=[GET])
def get_block_count():
    message, status = node.get_block_count()
    return make_response(message, status)
