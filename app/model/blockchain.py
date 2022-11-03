from model.block import Block
from hashlib import sha256
import json

BLOCKCHAIN_FILENAME = 'blockchain.txt'
SHA_SIZE = 256

class Blockchain:
    def __init__(self, files_path, log, difficulty_bits):
        self.__log = log
        self.__files_path = files_path
        self.__blockchain_head = None
        self.__target = 2 ** (SHA_SIZE - difficulty_bits)
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
            genesis_nonce = 438792
            genesis_data = [{'genesis_block': 'initial_message'}]
            self.__blockchain_head = Block(None, genesis_nonce, genesis_data, None)
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
            json_block["data"],
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
                return False
        # 2nd check: hash(block) must meet expected target
        if int(block.get_hash(), 16) < self.__target:
            return False
        return True

    """
    Add candidate block at the beginning of blockchain
    """
    def add_block(self, block):
        if self.__valid_block(block, self.__blockchain_head):
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
