from flask import Flask, jsonify, request
from model.key_manager import KeyManager
from requests import post
from ecdsa import BadSignatureError, VerifyingKey
import logging
import json
import os
import base64



SECRET = "SECRET"
SALT = "SALT"
FILES_PATH = "FILES_PATH"

GET = "GET"
POST = "POST"

OK = '200'
ERROR = '400'

app = Flask(__name__, static_url_path="")
log = app.logger

key_manager = KeyManager(os.environ.get(SECRET), os.environ.get(SALT), os.environ.get(FILES_PATH), log)

log.debug(f"Starting key list: {key_manager.get_pub_key_list()}")


@app.route('/pub-key-list', methods=[GET])
def index():
    message_json = json.dumps(key_manager.get_pub_key_list())
    return message_json, OK


@app.route('/connect', methods=[POST])
def connect():
    request_data = request.json
    ip = request_data['ip']
    
    log.info(f"Received request to join new network, target node: {ip}")
    
    body = key_manager.get_pub_key_list()
    
    try:
        log.info(f"Sending request to join network to target node: {ip}")
        res = post(format_ip(ip, 'join'), json = body)
            
        if res.ok:
            log.info(f"Sucessfully joined new network, received {res.content}")
            return jsonify(key_manager.get_pub_key_list()), OK
        
    except Exception as e:
        log.error(f"Error connecting to network, target node: {ip}, exception: {e}")
        return f"Error connecting to network", ERROR

    
    
@app.route('/join', methods=[POST])
def join():
    request_data = request.json
    log.info(f"Received request to join nodes to current network, received {request_data}")
    
    try:
        key_manager.update_pub_key_list(request_data)
        log.info(f'New entires added to current public key list')
    
    except Exception as e:
        error_mes = f"Error on saving new entries in public key list, error: {e}" 
        log.error(error_mes)
        return error_mes, ERROR

    result, ip = request_pub_key_list_updates()

    if not result:
        return f"Error updating list for address {ip}", ERROR
    
    return 'Successfully added new node(s) to network', OK


@app.route('/update', methods=[POST])
def update():
    request_data = request.json
    log.info(f"Received request to update public key list, new list: {request_data}")
    
    try:
        key_manager.override_pub_key_list(request_data)     
        log.info(f"List updated succesfully")
        return OK
    
    except Exception as e:
        log.error(f"Error encountered during call to update list, error: {e}")    
        return ERROR


@app.route('/send_message', methods=[POST])
def send_message():
    request_data = request.json
    ip = request_data['ip']
    message = request_data['message']

    signed_message = key_manager.get_private_key().sign(message.encode('utf-8')) 
    
    body = {
        "ip": key_manager.get_curr_ip(), 
        "signed_message": base64.b64encode(signed_message).decode('utf-8'),
        "plaintext": message
    }

    try:
        res = post(format_ip(ip, '/receive_message'), json = body)
        
        if res.ok:
            log.info(f"Got: {res.content}")
            return res.content, OK
            
    except Exception as e:
        error_mes = f"Error encountered during call to receive message, error: {e}" 
        log.error(error_mes)
        return error_mes, ERROR

    return "Error sending message"

@app.route('/receive_message', methods=[POST])
def receive_message():
    request_data = request.json
    ip = request_data['ip'] 
    signed_message = request_data['signed_message']
    plaintext = request_data['plaintext']

    try:
        if verify_sender(ip, signed_message, plaintext):
            body = {
                "confirmation":"OK",
                "message_from_veryfier":"You sign message using your private key",
                "sended_message": plaintext
            }
            return body

    except Exception as e:
        error_mes = f"Error encountered during veryfing message, error: {e}" 
        log.error(error_mes)
        return error_mes, ERROR


def request_pub_key_list_updates():
    pub_key_list = key_manager.get_pub_key_list()
    pub_key_list_length = len(pub_key_list) - 1 # minus current node's ip

    log.info(f"Starting process for updating connected nodes' public key lists, node count: {pub_key_list_length}")
    
    for el in pub_key_list['entries']:
        res = request_pub_key_list_update(el['ip'], pub_key_list)
        
        if not res:
            log.info(f"Public key update process failed")
            return False, el['ip']
        
    return True, None


def format_ip(ip, endpoint):
    return f"{ip}/{endpoint}"


def request_pub_key_list_update(ip, body):
    if ip != key_manager.get_curr_ip():
        log.info(f"Requesting pub key update for ip {ip}")
        try:
            res = post(format_ip(ip, 'update'), json = body)
            return True if res.ok else False
            
        except Exception as e:
            log.error(f"Pub key request for ip {ip} failed, reason: {e}")
            return False
        
    log.info(f"Ip matches host's ip, skipping")
    return True


def verify_sender(ip, signed_message, message):
    pub_key = key_manager.get_pub_key_for_ip(ip)
    if pub_key is None:
        return False
    try:
        vk = VerifyingKey.from_pem(pub_key)
        decrypted_message = base64.b64decode(signed_message.encode('utf-8'))

        return vk.verify(decrypted_message, message.encode('utf-8'))

    except BadSignatureError as e:
        log.error(f"Veryfing massage failed, reason: {e}")
        return False
