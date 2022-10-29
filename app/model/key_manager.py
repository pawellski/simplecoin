from ecdsa import SigningKey, VerifyingKey, NIST384p
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from os import environ
import base64, json

import logging

KEYS_FILENAME = 'keys.json'

class KeyManager:
    def __init__(self, secret, salt, files_path, log):
        self.__log = log
        self.__priv_key = None
        self.__pub_key = None
        self.__secret = secret
        self.__salt = salt
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
        kdf = PBKDF2(self.__secret.encode('utf-8'), self.__salt, dkLen=32)
        aes = AES.new(kdf, AES.MODE_ECB)
        keys['priv_key'] = base64.b64encode(aes.encrypt(pad(self.__priv_key.to_pem(), 16))).decode('utf-8')
        return keys

    def __load_keys(self, keys):
        self.__pub_key = VerifyingKey.from_pem(base64.b64decode(keys['pub_key'].encode('utf-8')))
        kdf = PBKDF2(self.__secret.encode('utf-8'), self.__salt, dkLen=32)
        aes = AES.new(kdf, AES.MODE_ECB)
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

    def get_private_key(self):
        return self.__priv_key
    
    def get_public_key(self):
        return self.__pub_key

    def get_curr_ip(self):
        return self.__ip

    def update_pub_key_list(self, new_pub_key_list):
        for entry in new_pub_key_list['entries']:
            if entry in self.__pub_key_list['entries']:
                continue
            self.__pub_key_list['entries'].append(entry)

    def override_pub_key_list(self, new_pub_key_list):
        self.__pub_key_list = new_pub_key_list
    
    def get_pub_key_list(self):
        return self.__pub_key_list

    def get_pub_key_for_ip(self, ip_without_port):
        for entry in self.__pub_key_list['entries']:
            if ip_without_port in entry['ip']:
                return entry['pub_key']
        return None
