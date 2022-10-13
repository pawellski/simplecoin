from flask import Flask, make_response
from model.key_manager import KeyManager
import logging
import json
import os

SECRET = "SECRET"
SALT = "SALT"
FILES_PATH = "FILES_PATH"

GET = "GET"

app = Flask(__name__, static_url_path="")

log = app.logger


@app.route('/keys', methods=[GET])
def index():
    key_manager = KeyManager(os.environ.get(SECRET), os.environ.get(SALT), os.environ.get(FILES_PATH), log)
    return {}, 200
