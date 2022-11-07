from ecdsa import SigningKey, VerifyingKey, NIST384p, BadSignatureError
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from requests import post
from os import environ
import base64, json
from flask import jsonify

import logging

KEYS_FILENAME = 'keys.json'

class KeyManager:
    def __init__(self, secret, files_path, log):
        self.__log = log
        self.__priv_key = None
        self.__pub_key = None
        self.__secret = secret
        self.__files_path = files_path
        self.__ip = f"http://{environ['NODE_IP']}"
        self.__pub_key_list = { 
            'entries': []
        }
        self.__get_keys()
        self.__init_network()
    
    def __get_keys(self):
        keys = self.__read_keys()
        if 'priv_key' not in keys or 'pub_key' not in keys:
            self.__log.info("generating keys...")
            keys = self.__generate_keys()
            self.__save_keys(keys)
        else:
            self.__log.info("loading keys...")
            self.__load_keys(keys)

    def __generate_keys(self):
        self.__priv_key = SigningKey.generate(curve=NIST384p)
        self.__pub_key = self.__priv_key.verifying_key
        self.__log.info(self.__priv_key.to_pem())
        self.__log.info(self.__pub_key.to_pem())
        keys = {}
        keys['pub_key'] = base64.b64encode(self.__pub_key.to_pem()).decode('utf-8')
        salt = get_random_bytes(16)
        kdf = PBKDF2(self.__secret.encode('utf-8'), salt, dkLen=32)
        iv = get_random_bytes(16)
        aes = AES.new(kdf, AES.MODE_CBC, iv)
        keys['priv_key'] = base64.b64encode(aes.encrypt(pad(self.__priv_key.to_pem(), 16))).decode('utf-8')
        keys['extra'] = base64.b64encode(salt + iv).decode('utf-8')
        return keys

    def __load_keys(self, keys):
        self.__pub_key = VerifyingKey.from_pem(base64.b64decode(keys['pub_key'].encode('utf-8')))
        salt = base64.b64decode(keys['extra'].encode('utf-8'))[0:16]
        iv = base64.b64decode(keys['extra'].encode('utf-8'))[16:32]
        kdf = PBKDF2(self.__secret.encode('utf-8'), salt, dkLen=32)
        aes = AES.new(kdf, AES.MODE_CBC, iv)
        self.__priv_key = SigningKey.from_pem(unpad(aes.decrypt(base64.b64decode(keys['priv_key'].encode('utf-8'))), 16).decode('utf-8'))
        self.__log.info(self.__priv_key.to_pem())
        self.__log.info(self.__pub_key.to_pem())
    
    def __save_keys(self, keys):
        with open(f"{self.__files_path}/{KEYS_FILENAME}", 'w') as file:
            json.dump(keys, file)

    def __read_keys(self):
        try:
            with open(f"{self.__files_path}/{KEYS_FILENAME}", 'r') as file:
                keys = json.load(file)
            return keys
        except FileNotFoundError as e:
            return {}

    def __init_network(self):
        self.__log.info("init network...")
        self.__pub_key_list['entries'].append({
            'ip': self.__ip,
            'pub_key': self.__pub_key.to_pem().decode('utf-8')
        })

    def __get_pub_key_for_ip(self, ip_without_port):
        for entry in self.__pub_key_list['entries']:
            if ip_without_port in entry['ip']:
                return entry['pub_key']
        return None

    def __format_ip(self, ip, endpoint):
        return f"{ip}/{endpoint}"

    def __request_pub_key_list_update(self, ip):
        if ip != self.__ip:
            self.__log.info(f"Requesting pub key update for ip {ip}")
            try:
                res = post(self.__format_ip(ip, 'update'), json = self.__pub_key_list)
                return True if res.ok else False

            except Exception as e:
                self.__log.error(f"Pub key request for ip {ip} failed, reason: {e}")
                return False

        self.__log.info(f"Ip matches host's ip, skipping")
        return True

    def __update_pub_key_list(self, new_pub_key_list):
        for entry in new_pub_key_list['entries']:
            if entry in self.__pub_key_list['entries']:
                continue
            self.__pub_key_list['entries'].append(entry)

    def __override_pub_key_list(self, new_pub_key_list):
        self.__pub_key_list = new_pub_key_list

    def __request_pub_key_list_updates(self):
        self.__log.info(f"Starting process for updating connected nodes' public key lists, node count: {len(self.__pub_key_list) - 1}") # minus current node's ip
        for el in self.__pub_key_list['entries']:
            res = self.__request_pub_key_list_update(el['ip'])
            if not res:
                self.__log.info(f"Public key update process failed")
                return False, el['ip']
        return True, None

    def __verify_sender(self, ip, signed_message, message):
        pub_key = self.__get_pub_key_for_ip(ip)
        if pub_key is None:
            return False
        try:
            vk = VerifyingKey.from_pem(pub_key)
            decrypted_message = base64.b64decode(signed_message.encode('utf-8'))
            return vk.verify(decrypted_message, message.encode('utf-8'))

        except (BadSignatureError, TypeError) as e:
            self.__log.error(f"Veryfing massage failed, reason: {e}")
            return False

    def __sign_message(self, message):
        return self.__priv_key.sign(message.encode('utf-8'))

    def get_pub_key_list(self):
        return self.__pub_key_list

    def get_own_ip(self):
        return self.__ip

    def connect(self, request_data):
        ip = request_data['ip']
        self.__log.info(f"Received request to join new network, target node: {ip}")
        body = self.get_pub_key_list()

        try:
            self.__log.info(f"Sending request to join network to target node: {ip}")
            res = post(self.__format_ip(ip, 'join'), json = body)
            if res.ok:
                self.__log.info(f"Sucessfully joined new network, received {res.content}")
                return jsonify(self.get_pub_key_list())
        except Exception as e:
            error_message = f"Error connecting to network, target node: {ip}, exception: {e}"
            self.__log.error(error_message)
            e.message = error_message
            raise

    def join(self, request_data):
        self.__log.info(f"Received request to join nodes to current network, received {request_data}")
        try:
            self.__update_pub_key_list(request_data)
            self.__log.info(f'New entires added to current public key list')
        except Exception as e:
            error_message = f"Error on saving new entries in public key list, error: {e}"
            self.__log.error(error_message)
            e.message = error_message
            raise
        result, ip = self.__request_pub_key_list_updates()
        if not result:
            raise Exception(f"Error updating list for address {ip}")
        return "Successfully added new node(s) to network"

    def send_message(self, request_data):
        ip = request_data['ip']
        message = request_data['message']
        signed_message = self.__sign_message(message)

        body = {
            "signed_message": base64.b64encode(signed_message).decode('utf-8'),
            "plaintext": message
        }

        try:
            res = post(self.__format_ip(ip, '/verify-message-from-node'), json = body)
            if res.ok:
                self.__log.info(f"Got: {res.content}")
                return res.content
            else:
                raise Exception("Error sending message")
        except Exception as e:
            e.message = f"Error encountered during call to receive message, error: {e}"
            raise


    def receive_message(self, request_data, addressee_ip):
        signed_message = request_data['signed_message']
        plaintext = request_data['plaintext']

        try:
            body = {}
            if self.__verify_sender(addressee_ip, signed_message, plaintext):
                body['confirmation'] = 'True'
                body['message_from_veryfier'] = 'Message signed correctly'
            else:
                body['confirmation'] = 'False'
                body['message_from_veryfier'] = 'Message signed incorrectly'
            body['sended_message'] = plaintext
            return jsonify(body)
        except Exception as e:
            e.message = f"Error encountered during veryfing message, error: {e}"
            raise

    def update(self, request_data):
        self.__log.info(f"Received request to update public key list, new list: {request_data}")
        try:
            self.__override_pub_key_list(request_data)
            return "List updated succesfully"
        except Exception as e:
            e.message = f"Error encountered during call to update list, error: {e}"
            raise











    def sign_transaction_message(self, request_data):
        message = request_data['message']
        signed_message = self.__sign_message(message)

        body = {
            "signed_message": base64.b64encode(signed_message).decode('utf-8')
        }

        try:
            res = post(self.__format_ip(self.__ip, '/broadcast_transaction_message'), json = body)
            if res.ok:
                self.__log.info(f"Transaction message has been broadcasted: {res.content}")
                return res.content
            else:
                raise Exception("Error sending transaction message to be broadcasted")
        except Exception as e:
            e.message = f"Error encountered during call to broadcast transacion message, error: {e}"
            raise


    def broadcast_transaction_message(self, transaction_message):
        self.__log.info(f"Received request to broadcast new transaction message")
   
        result, ip = self.__requests_transaction_message_broadcast(transaction_message)
        if not result:
            raise Exception(f"Error broadcasting transaction message to {ip}")
        return "Successfully broadcasted transaction message"



    def __requests_transaction_message_broadcast(self, transaction_message):
        self.__log.info(f"Starting process for broadcasting transaction message")

        for el in self.__pub_key_list['entries']:
            res = self.__request_transaction_message_broadcast(el['ip'], transaction_message)
            if not res:
                self.__log.info(f"Transaction message broadcast process failed")
                return False, el['ip']
        return True, None


    def __request_transaction_message_broadcast(self, ip, transaction_message):
        self.__log.info(f"Requesting transaction message broadcast for ip {ip}")
        try:
            res = post(self.__format_ip(ip, '/update-transaction-pool'), json = transaction_message)
            return True if res.ok else False

        except Exception as e:
            self.__log.error(f"Transaction message broadcast for ip {ip} failed, reason: {e}")
            return False



################### TESTING ##################
    def update_transaction_pool(self, ip, request_data):
        self.__log.info(f"!!!!!!!!!  TRANSACTION POOL UPDATED   !!!!!!!!!")
        return True