from hashlib import sha256
from time import time
from model.genesis_data import GENESIS_DATA
from model.transaction import Transaction
from model.block import Block
import json


BLOCKCHAIN_FILENAME = 'blockchain.txt'
SHA_SIZE = 256
GENESIS_DATA_FILENAME = 'genesis_data.txt'
class Blockchain:
    def __init__(self, files_path, log, difficulty_bits):
        self.__log = log
        self.__files_path = files_path
        self.__blockchain_head = None
        self.__target = 2 ** (SHA_SIZE - difficulty_bits)
        self.__time = time()
        self.__get_blockchain()

    """
    Fetch or create blockchain at the beginning
    """
    def __get_blockchain(self):
        # read blockchain from file
        self.__read_blockchain()
        # if file not contain blockchain, genesis block will be created
        if self.__blockchain_head is None:
            self.__log.info("Create first block...")
            transactions = []
            for t in GENESIS_DATA['data']:
                transactions.append(Transaction.from_dict_to_transaction(t))
            self.__blockchain_head = Block(
                None,
                GENESIS_DATA['header']['nonce'],
                transactions,
                None
            )
            self.__log.info(self.__blockchain_head.get_data().get_transactions())
            self.__save_one_block(self.__blockchain_head)
        else:
            self.__log.info("Blockchain was loaded")

    """
    Fetch or create blockchain after launch app 
    """
    def __read_blockchain(self):
        try:
            with open(f"{self.__files_path}/{BLOCKCHAIN_FILENAME}", 'r') as file:
                json_str = ''
                for line in file.read().splitlines():
                    # every block is separated by hash character
                    if line == '#':
                        # add block as a head to blockchain
                        self.__set_head_block(json_str)
                        json_str = ''
                    else:
                        json_str += line.strip()
        except FileNotFoundError:
            self.__log.debug("Blockchain file {self.__files_path}/{BLOCKCHAIN_FILENAME} not found")
        except json.decoder.JSONDecodeError:
            self.__log.debug("Incorrect format of json")

    """
    Create block after reading and set as a head
    """
    def __set_head_block(self, json_str_block):
        json_block = json.loads(json_str_block)
        block = Block (
            json_block["header"]["previous_block_hash"],
            json_block["header"]["nonce"],
            [Transaction.from_dict_to_transaction(t) for t in json_block["data"]],
            self.__blockchain_head
        )
        self.__blockchain_head = block

    """
    Save blockchain to file,
    every block is a json and blocks are separeted by #
    """
    def __save_blockchain(self):
        block = self.__blockchain_head
        try:
            open(f"{self.__files_path}/{BLOCKCHAIN_FILENAME}", 'w').close()
            with open(f"{self.__files_path}/{BLOCKCHAIN_FILENAME}", 'a') as file:
                while block is not None:
                    json.dump(block.to_dict(), file, indent=4)
                    file.write("\n#\n")
                    block = block.get_previous_block()
        except FileNotFoundError:
            self.__log.debug("Block was not saved - file {self.__files_path}/{BLOCKCHAIN_FILENAME} not found")

    """
    Save one block to blockchain file,
    new block (head) is saved at the end of the blockchain file
    """
    def __save_one_block(self, block):
        try:
            with open(f"{self.__files_path}/{BLOCKCHAIN_FILENAME}", 'a') as file:
                json.dump(block.to_dict(), file, indent=4)
                file.write("\n#\n")
        except FileNotFoundError:
            self.__log.debug("Block was not saved - file {self.__files_path}/{BLOCKCHAIN_FILENAME} not found")

    """
    Return True if block is correctly
    otherwise return False
    """
    def __valid_block(self, block, previous_block):
        if block is None:
            return False
        # 1st check: previous block hash in block must be equaled with hash(previous_block)
        if previous_block is not None:
            if block.get_header().get_previous_block_hash() != previous_block.get_hash():
                self.__log.error(f"Hashes dont match, head: {previous_block.get_hash()}, candidate: {block.get_header().get_previous_block_hash()}")
                return False
        # 2nd check: hash(block) must meet expected target
        if int(block.get_hash(), 16) >= self.__target:
            self.__log.error(f"Candidate does not meet target requirements, hash: {block.get_hash()} target: {self.__target}")
            return False
        return True

    def add_block(self, block=None, block_dict=None):
        new_time = time()
        self.__log.info(f'New candidate await time: {new_time - self.__time}')
        self.__time = new_time
        if block_dict is not None:
            block = Block(
                previous_block_hash=block_dict['header']['previous_block_hash'],
                transactions=[Transaction.from_dict_to_transaction(t) for t in block_dict['data']],
                nonce=block_dict['header']['nonce'],
                previous_block=None
            )
        self.__log.info("Saving new candidate")
        # add new block (head) to blockchain if validation is correct
        if self.__valid_block(block, self.__blockchain_head):
            # self.__log.info("New candidate validated")
            block.set_previous_block(self.__blockchain_head)
            self.__blockchain_head = block
            self.__save_one_block(block)
            return True
        else:
            return False

    """
    Verify blockchain block by block,
    verification bases on __valid_block function
    """
    def verify_blockchain(self):
        block = self.__blockchain_head
        # verify every block from head to genesis block
        while block is not None:
            if self.__valid_block(block, block.get_previous_block()) is False:
                return "Blockchain verified incorrectly"
            # change reference to verified block in direction of the beginning
            block = block.get_previous_block()
        return "Blockchain verified correctly"

    def get_blockchain_head(self):
        return self.__blockchain_head

    def get_previous_block(self, block):
        return block.get_previous_block()

    def get_block_count(self):
        count = 0
        current_block = self.get_blockchain_head()
        while current_block is not None:
            count += 1
            current_block = current_block.get_previous_block()
        return {"count": count}
