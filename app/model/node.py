from threading import Thread
from model.key_manager import KeyManager
from model.message_generator import MessageGenerator
from model.blockchain import Blockchain
from model.miner import Miner
import json

OK = 200
ERROR = 400

DIFFICULTY_BITS = 20


class Node:
    def __init__(self, secret, files_path, log):
        self.__key_manager = KeyManager(secret, files_path, log)
        self.__message_generator = MessageGenerator(log, self.__key_manager)
        self.__blockchain = Blockchain(files_path, log, DIFFICULTY_BITS)
        self.__miner = Miner(log, DIFFICULTY_BITS, self.__blockchain, self.__key_manager)
        self.__current_candidate = None

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

    def verify_message_from_node(self, request_data, addressee_ip):
        try:
            return self.__key_manager.receive_message(request_data, addressee_ip), OK
        except Exception as e:
            return str(e), ERROR

    def verify_blockchain(self):
        return self.__blockchain.verify_blockchain(), OK

    def start_generator(self, request):
        try:
            return self.__message_generator.start_generator(request), OK
        except Exception as e:
            return str(e), ERROR

    def stop_generator(self):
        try:
            return self.__message_generator.stop_generator(), OK
        except Exception as e:
            return str(e), ERROR

    def start_miner(self):
        return self.__miner.start_miner(), OK

    def update_transaction_pool(self, request_data):
        try:
            return self.__miner.append_transaction(request_data), OK
        except Exception as e:
            return str(e), ERROR

    def verify_and_save_candidate(self, request_data):
        self.__current_candidate = request_data
        thread = Thread(
            target=self.__verify_and_save_candidate
        )
        thread.start()
        return "Candidate received", OK

    def stop_miner(self):
        self.__miner.stop_miner()
        return "Miner paused", OK

    def __verify_and_save_candidate(self):
        request_data = self.__current_candidate
        block_added = self.__blockchain.add_block(block_dict=request_data)
        self.__miner.reset_miner_after_new_candidate_request(block_added)
