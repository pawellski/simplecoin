from flask import Flask, make_response, jsonify, request
from model.key_manager import KeyManager
from requests import post
import logging
import json
import os

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
    
    body = {
        "ip": key_manager.get_curr_ip(),
        "pub_key": key_manager.get_public_key().to_pem().decode('UTF-8')
    }
    
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
        key_manager.save_new_pub_key(request_data)
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
        key_manager.update_pub_key_list(request_data)     
        log.info(f"List updated succesfully")
        return OK
    
    except Exception as e:
        log.error(f"Error encountered during call to update list, error: {e}")    
        return ERROR



def request_pub_key_list_updates():
    pub_key_list = key_manager.get_pub_key_list()
    pub_key_list_length = len(pub_key_list) - 1 # minus current node's ip

    log.info(f"Starting process for updating connected nodes' public key lists, node count: {pub_key_list_length}")
    
    for el in pub_key_list['entries']:
        res = request_pub_key_list_update(el['ip'], pub_key_list)
        
        if not res:
            log.info(f"Public key pdate process failed")
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