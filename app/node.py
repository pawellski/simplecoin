from flask import Flask, make_response
import logging, json

GET = "GET"

app = Flask(__name__, static_url_path="")

log = app.logger

public_keys = { }

@app.route('/', methods=[GET])
def index():
    message_json = json.dumps(public_keys)
    return message_json, 200
