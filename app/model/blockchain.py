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
        self.__blockchain_head = []
        self.__target = 2 ** (SHA_SIZE - difficulty_bits)
        self.__time = time()
        self.__get_blockchain()
        self.__orphan_list = []

    """
    Fetch or create blockchain at the beginning
    """
    def __get_blockchain(self):
        # read blockchain from file
        # self.__read_blockchain()
        # if file not contain blockchain, genesis block will be created
        if not self.__blockchain_head:
            self.__log.info("Create first block...")
            transactions = []
            for t in GENESIS_DATA['data']:
                transactions.append(Transaction.from_dict_to_transaction(t))
            self.__blockchain_head.append(Block(
                None,
                GENESIS_DATA['header']['nonce'],
                transactions,
                None
            ))
            self.__log.info(self.__blockchain_head[0].get_data().get_transactions())
            self.__save_one_block(self.__blockchain_head[0])
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
        self.__blockchain_head.append(block)

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
    def __valid_blockchain(self, block, previous_block):
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


    """
    Return True if block is correctly
    otherwise return False
    """
    def __valid_block(self, block):
        if block is None:
            return False
        else:    
            # Check: hash(block) must meet expected target
            if int(block.get_hash(), 16) >= self.__target:
                self.__log.error(f"Candidate does not meet target requirements, hash: {block.get_hash()} target: {self.__target}")
                return False
        return True
    
    '''
    Searching of candidate's parent
    Checking if any of blocks' hash in blockchain is a previous block hash of candidate block
    '''
    def __is_orphan_block(self, block):                       
        for head in self.__blockchain_head:
            block_from_blockchain = head
            # verify every block from head to genesis block to find parent of new block
            while block_from_blockchain is not None:
                if block.get_header().get_previous_block_hash() == block_from_blockchain.get_hash():
                    self.__log.info(f"Block has parent")
                    block.set_previous_block(block_from_blockchain)
                    return False, block
                # change reference to verified block in direction of the beginning
                block_from_blockchain = block_from_blockchain.get_previous_block()
        self.__log.info(f"Block is orphan")
        return True, block

    '''
    Validation if hash(block) meets expected target and if it is correct than checking if block is an orphan
    '''
    def check_block(self, block_dict=None):
        if block_dict is not None:
            block = Block(
                previous_block_hash=block_dict['header']['previous_block_hash'],
                transactions=[Transaction.from_dict_to_transaction(t) for t in block_dict['data']],
                nonce=block_dict['header']['nonce'],
                previous_block=None
            )

            if self.__valid_block(block):
                self.__log.info(f"Block is valid")
                is_orphan, block_after_check = self.__is_orphan_block(block)
                return True, is_orphan, block_after_check
            else:
                return False, False, block
    '''
    Steps of addition a new block to orphan list:
    1. Check if block has a family in orphan list
    2. Check if new block is a parent and child at the same time - check parent of head and root block
    '''
    def add_to_orphan_list(self, block):
        if block is not None:
            #1
            has_family, is_parent, is_child, orphan_blocks_to_add, orphan_blocks_to_remove = self.__is_part_of_family(block)
            if has_family:
                for block_to_add in orphan_blocks_to_add:
                    self.__orphan_list.append(block_to_add)
                            
                for block_to_remove in orphan_blocks_to_remove:
                    self.__orphan_list.remove(block_to_remove)
            #2
                if is_parent and is_child:
                    orphan_blocks_to_remove = []
                    for orphan_head in self.__orphan_list:
                        for el in self.__orphan_list:
                            orphan_block = el
                            if orphan_head.get_hash() == orphan_block.get_header().get_previous_block_hash():
                                orphan_blocks_to_remove.append(orphan_head)
                                break
                            while orphan_block is not None:
                                if orphan_block.get_previous_block() == None:
                                    if orphan_head.get_hash() == orphan_block.get_header().get_previous_block_hash():
                                        orphan_blocks_to_remove.append(orphan_head)                        
                                orphan_block = orphan_block.get_previous_block()

                    for block_to_remove in orphan_blocks_to_remove:
                        self.__orphan_list.remove(block_to_remove)
                    self.__log.info(f"Orphan list has been filtred through blocks that was parent and child")
            else:
                self.__orphan_list.append(block)

    '''
    Steps of checking if block is a family member:
    1. Check if new block is a parent of existing block in orphan list
    2. Check if new block is a child of existing block in orphan list
    3. Check if new block is a child of block from one of orphan's family member
    4. Check if new block is a parent of root block from one of orphan's family member
    '''
    def  __is_part_of_family(self, new_block):   
        orphan_blocks_to_add = []
        orphan_blocks_to_remove = []
        is_parent = False
        is_child = False

        if self.__orphan_list:
            for orphan_head in self.__orphan_list:
                #1
                if orphan_head.get_previous_block() == None and \
                    new_block.get_hash() == orphan_head.get_header().get_previous_block_hash():
                    self.__log.info(f"New OrphanBlock is parent of block in orphan list")
                    orphan_block.set_previous_block(new_block)
                    is_parent = True
                    continue
                #2, 3
                orphan_block = orphan_head
                while orphan_block is not None:
                    if new_block.get_header().get_previous_block_hash() == orphan_block.get_hash():
                        self.__log.info(f"New OrphanBlock has parent in orphan list")
                        new_block.set_previous_block(orphan_block)
                        orphan_blocks_to_add.append(new_block)
                        is_child = True
                        if orphan_block == orphan_head:
                            orphan_blocks_to_remove.append(orphan_block)
                            return True, is_parent, is_child, orphan_blocks_to_add, orphan_blocks_to_remove
                        return True, is_parent, is_child, orphan_blocks_to_add, orphan_blocks_to_remove
                #4
                    if orphan_block.get_previous_block() == None:
                        if new_block.get_hash() == orphan_block.get_header().get_previous_block_hash():
                            self.__log.info(f"New OrphanBlock is parent of root block from one block in orphan list")
                            orphan_block.set_previous_block(new_block)
                            is_parent = True
                            return True, is_parent, is_child, orphan_blocks_to_add, orphan_blocks_to_remove

                    orphan_block = orphan_block.get_previous_block()        

        self.__log.info(f"New OrphanBlock doesnt have family in orphan list")
        return False, is_parent, is_child, orphan_blocks_to_add, orphan_blocks_to_remove

    '''
    Steps of addition the new block to blockchain:
    1. Check if new block is parent of root block of each block in orphan list
    2. Add new block to file and if is a parent than add all blocks, from root to youngest child, to file 
    3. If new block is not a parent it is automatically a new head of blockchain, 
        if new block is a parent his youngest childs are heads (removing old head if his parent was a head and save new head)
    4. If is a parent than remove orphan_head, which is his youngest family member, from orphan list
    '''
    def add_block(self, new_block):
        orphan_blocks_to_remove = []
        head_blocks_to_remove = []
        is_parent = False
        new_time = time()
        self.__log.info(f'New candidate await time: {new_time - self.__time}')
        self.__time = new_time
        new_head = None
        if new_block is not None:
            #1
            if self.__orphan_list:
                for orphan_head in self.__orphan_list:
                    orphan_block = orphan_head
                    while orphan_block is not None:
                        if orphan_block.get_previous_block() == None:
                            if new_block.get_hash() == orphan_block.get_header().get_previous_block_hash():
                                self.__log.info(f"New Block is parent of root block from one/few blocks in orphan list")
                                orphan_block.set_previous_block(new_block)
                                orphan_blocks_to_remove.append(orphan_head)
                                new_head = orphan_head
                                is_parent = True
                        orphan_block = orphan_block.get_previous_block()        

            if not is_parent:
                self.__log.info(f"Block is not a parent of any orphan blocks")
                new_head = new_block
            #2
            self.__log.info("Saving new candidate")
            self.__save_one_block(new_block)
            for block_to_remove in orphan_blocks_to_remove:
                orphan_to_blockchain = block_to_remove.get_previous_block()
                while new_block.get_hash() != orphan_to_blockchain.get_header().get_previous_block_hash():
                    self.__save_one_block(orphan_to_blockchain)
                orphan_to_blockchain = orphan_to_blockchain.get_previous_block()
            #3
            for head in self.__blockchain_head:
                if new_block.get_header().get_previous_block_hash() == head.get_hash():
                    self.__log.info(f"Head blocks list is being updated")
                    head_blocks_to_remove.append(head)
            self.__blockchain_head.append(new_head) 
            
            self.__log.info(f"NUMBER OF HEADS before update = {len(self.__blockchain_head)}")
            for block_to_remove in head_blocks_to_remove:
                self.__blockchain_head.remove(block_to_remove)
            self.__log.info(f"NUMBER OF HEADS after update = {len(self.__blockchain_head)}") 
            #4
            for block_to_remove in orphan_blocks_to_remove:
                self.__orphan_list.remove(block_to_remove)

    """
    Verify blockchain block by block,
    verification bases on __valid_blockchain function
    """
    def verify_blockchain(self):
        block = self.__blockchain_head
        # verify every block from head to genesis block
        while block is not None:
            if self.__valid_blockchain(block, block.get_previous_block()) is False:
                return "Blockchain verified incorrectly"
            # change reference to verified block in direction of the beginning
            block = block.get_previous_block()
        return "Blockchain verified correctly"

    def get_blockchain_head_list(self):
        return self.__blockchain_head

    def get_blockchain_head(self):
        longest_blockchain = self.__get_longest_blockchain()
        return longest_blockchain

    def get_orphan_list(self):
        return self.__orphan_list

    def get_previous_block(self, block):
        return block.get_previous_block()

    def get_block_count(self, concrete_branch_head=None):
        count = 0
        if concrete_branch_head is not None:
            current_block = concrete_branch_head
        else:
            current_block = self.get_blockchain_head()
        while current_block is not None:
            count += 1
            current_block = current_block.get_previous_block()
        return {"count": count}

    '''
    Return currently the longest branch of blockchain
    '''
    def __get_longest_blockchain(self):
        head_and_count = {}
        count = 0
        block_head = self.__blockchain_head
        for head in block_head:
            current_block = head
            while current_block is not None:
                count += 1
                current_block = current_block.get_previous_block()
            head_and_count[head] = count
        longest_blockchain = max(head_and_count, key = head_and_count.get)
        return longest_blockchain
    
    '''
    Get all branches from blockchain's heads and visualize it on website
    '''
    def visualize_blockchain(self):
        tree_struct = []
        blockchain_head = self.__blockchain_head
        for head in blockchain_head:
            block = head
            count = self.get_block_count(head)['count'] - 1
            while block is not None:
                message = 'Block head' if block == head else f"Block {count}"
                item = {'name': block.get_hash(), 
                        'manager': block.get_header().get_previous_block_hash(),
                        'toolTip': '',
                        'body': block.to_dict(True), 
                        'message': message if block.get_previous_block() != None else 'Genesis block'
                        }
                count -= 1        
                tree_struct.append(item)        
                block = block.get_previous_block()
        return tree_struct
    
    '''
    Get all branches from orphan's heads and visualize it on website
    '''
    def visualize_orphan_list(self):
        tree_struct = []
        orphan_list_head = self.__orphan_list
        for head in orphan_list_head:
            block = head
            count = self.get_block_count(head)['count'] - 1
            while block is not None:
                message = 'Orphan block head' if block == head else f"Orphan block {count}"
                item = {'name': block.get_hash(),
                        'manager': block.get_header().get_previous_block_hash(),
                        'toolTip': '',
                        'body': block.to_dict(True), 
                        'message': message if block.get_previous_block() != None else 'Orphan root block'
                        }
                count -= 1    
                tree_struct.append(item)        
                block = block.get_previous_block()
        return tree_struct