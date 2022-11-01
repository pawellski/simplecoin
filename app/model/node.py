from model.key_manager import KeyManager
from model.message_generator import MessageGenerator
from model.blockchain import Blockchain
from model.miner import Miner
import json

OK = 200
ERROR = 400

class Node:
    def __init__(self, secret, files_path, log):
        self.__key_manager = KeyManager(secret, files_path, log)
        self.__message_generator = MessageGenerator(log)
        self.__blockchain = Blockchain(files_path, log)
        self.__miner = Miner(log)

    def get_pub_key_list(self):
        return json.dumps(self.__key_manager.get_pub_key_list()), OK

    def connect(self, request_data):
        try:
            return self.__key_manager.connect(request_data), OK
        except Exception as e:
            return str(e), ERROR

    def join_node(self, request_data):
        try:
            return self.__key_manager.join(request_data), OK
        except Exception as e:
            return str(e), ERROR

    def update_node(self, request_data):
        try:
            return self.__key_manager.update(request_data), OK
        except Exception as e:
            return str(e), ERROR

    def send_message_to_verification(self, request_data):
        try:
            return self.__key_manager.send_message(request_data), OK
        except Exception as e:
            return str(e), ERROR

    def verify_message_from_node(self, request_data):
        try:
            return self.__key_manager.receive_message(request_data), OK
        except Exception as e:
            return str(e), ERROR