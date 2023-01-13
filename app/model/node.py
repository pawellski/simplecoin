from threading import Thread
from model.block import Block
from model.transaction_tuples import OutputTuple
from model.wallet import Wallet
from model.key_manager import KeyManager
from model.message_generator import MessageGenerator
from model.blockchain import Blockchain
from model.miner import Miner
import json

OK = 200
ERROR = 400

DIFFICULTY_BITS = 19
MINER_REWARD = 0.005

class Node:
    def __init__(self, secret, files_path, log):
        self.__key_manager = KeyManager(secret, files_path, log)
        self.__blockchain = Blockchain(files_path, log, DIFFICULTY_BITS)
        self.__wallet = Wallet(self.__key_manager, self.__blockchain, log)
        self.__message_generator = MessageGenerator(log, self.__key_manager, self.__wallet)
        self.__miner = Miner(log, DIFFICULTY_BITS, self.__blockchain, self.__key_manager, self.__wallet, MINER_REWARD)
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

    def init_blockchain(self):
        transactions = []
        for entry in self.__key_manager.get_pub_key_list()['entries']:
            transactions.append(
                self.__wallet.makeup_transaction(
                    True,
                    OutputTuple(
                        entry['pub_key'],
                        entry['pub_key'],
                        100,
                        0
                    ),
                    0
                )
            )
        init_block = self.__miner.proof_of_work(transactions)
        self.__blockchain.add_block(init_block)

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

    def get_current_balance(self):
        balance = json.dumps({'current_balance': self.__wallet.check_balance()})
        return balance, OK

    def __verify_and_save_candidate(self):
        request_data = self.__current_candidate
        block_valid, is_orphan, block = self.__blockchain.check_block(block_dict=request_data)  #DONE
        if block_valid:
            duplicated_transaction = self.__miner.init_addition_of_candidate(request_data)             #TODO - filtration
            if is_orphan:           
                self.__blockchain.add_to_orphan_list(block)                                     #DONE
            else:
                self.__blockchain.add_block(block)                                              #DONE
            self.__miner.reset_miner_after_new_candidate_request(is_orphan)                     #DONE

    def get_block_count(self):
        count = self.__blockchain.get_block_count()
        return count, OK

    def visualize_blockchain(self):
        tree_struct = []
        blockchain_head = self.__blockchain.get_blockchain_head_list()
        for head in blockchain_head:
            block = head
            while block is not None:
                message = 'Some text to display at the bottom of the block' 
                item = {'name': block.get_hash(), # to jest ID bloku
                        'manager': block.get_header().get_previous_block_hash(), # to jest ID rodzica - jeżeli będzie kilka elementów listy, którzy mają tego samego rodzica, to wyświetli forka.
                        'toolTip': '',
                        'body': block.get_header().to_dict(), #json.dumps(block.to_dict()), # Generalnie to jest to co jest najbardziej widoczne
                        'message': message # to jest to na czerwono na dole bloku
                        }
                tree_struct.append(item)        
                block = block.get_previous_block()
        return tree_struct

    def visualize_orphan_list(self):
        tree_struct = []
        orphan_list_head = self.__blockchain.get_orphan_list()
        for head in orphan_list_head:
            block = head
            while block is not None:
                message = 'Some text to display at the bottom of the block' 
                item = {'name': block.get_hash(), # to jest ID bloku
                        'manager': block.get_header().get_previous_block_hash(), # to jest ID rodzica - jeżeli będzie kilka elementów listy, którzy mają tego samego rodzica, to wyświetli forka.
                        'toolTip': '',
                        'body': block.get_header().to_dict(), #json.dumps(block.to_dict()), # Generalnie to jest to co jest najbardziej widoczne
                        'message': message # to jest to na czerwono na dole bloku
                        }
                tree_struct.append(item)        
                block = block.get_previous_block()
        return tree_struct