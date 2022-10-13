from logging import Logger
from multiprocessing import Process, Queue
from threading import Thread
from random import randint
from requests import post

from model.block import Block
from model.blockchain import Blockchain
from model.key_manager import KeyManager


class Miner:
    def __init__(
        self,
        log: Logger,
        difficulty_bits: int,
        blockchain: Blockchain,
        key_manager: KeyManager
    ):
        self.__log = log
        self.__transaction_pool = []
        self.__blockchain = blockchain
        self.__key_manager = key_manager
        self.__max_nonce = 2 ** 32  # 4 billion
        self.__miner_process = None
        self.__miner_paused = True
        self.__difficulty_bits = difficulty_bits
        self.__miner_result_queue = Queue()
        self.__miner_thread = None
        self.__miner_thread_running = False

    def append_transaction(
        self,
        transaction: dict
    ):
        self.__log.debug("Appending trasaction")
        self.__transaction_pool.append(transaction)
        return "Transaction appended"

    '''
    Update head block after new candidate gets appended
    '''
    def reset_miner_after_new_candidate_request(self, block_added: bool):
        if block_added:
            self.__log.info("New block added, resetting miner")
            self.__reset_miner_process(
                self.__blockchain
                    .get_blockchain_head()
                    .get_data()
                    .get_transactions()
            )
        else:
            self.__reset_miner_process()

    '''
    Start miner thread
    Responsible for handling the miner process
    '''
    def start_miner(self):
        self.__log.info("Starting miner thread")
        self.__miner_paused = False
        self.__miner_thread_running = True
        self.__miner_thread = Thread(target=self.__start_mining)
        self.__miner_thread.start()
        return "Miner sucessfully started"

    def stop_miner(self):
        self.__stop_miner_process()
        self.__miner_thread_running = False
        self.__miner_thread.join()

    '''
    Send new candidate to nodes in the network
    '''
    def __broadcast_candidate(self, candidate: Block):
        self.__log.debug("Broadcasting new candidate block")
        for el in self.__key_manager.get_pub_key_list()['entries']:

            if el['ip'] != self.__key_manager.get_own_ip():
                try:
                    self.__log.debug(f"Sending candidate to {el['ip']}")
                    res = post(
                        self.__key_manager.format_ip(
                            el['ip'], '/save-candidate'
                        ),
                        json=candidate.to_dict()
                    )
                    if not res.ok:
                        self.__log.error(
                            f"Error sending candidate to node {el['ip']}, error: {res.content}"
                        ) 
                except Exception as e:
                    self.__log.error(
                        f"Error sending candidate to node {el['ip']}, error: {e}"
                    )
        self.__log.debug("New candidate broadcast finished")

    '''
    Stop the miner process
    '''
    def __stop_miner_process(self):
        self.__log.debug("Stopping miner process")
        self.__miner_paused = True
        if self.__miner_process is not None and \
           self.__miner_process.is_alive():
            self.__miner_process.terminate()

    '''
    Start the miner process
    Should be started on miner activation through adequate endpoint
    '''
    def __start_miner_process(self):
        self.__log.debug(
            "Starting miner process, "
            f"tranasction pool: {self.__transaction_pool}"
        )
        self.__miner_process = Process(
            target=self.__proof_of_work
        )
        self.__miner_process.start()
        self.__miner_paused = False

    '''
    Start miner process
    Assumes that the current batch of transaction pool has been processed
    Also ran on miner process initial startup
    '''
    def __reset_miner_process(self, new_block_transactions=None):
        # Kill miner process if alive
        self.__log.debug("Resetting miner process")
        self.__stop_miner_process()

        # Get diff between current transaction pool and new block transactions
        if new_block_transactions is not None:
            self.__log.debug("New block added - updating transaction pool")
            self.__transaction_pool = \
                [t for t in self.__transaction_pool
                 if not (t in new_block_transactions)]

        self.__miner_paused = False

    def __get_candidate_block(self) -> Block:
        return self.__miner_result_queue.get()

    '''
    Thread responsible for the miner process control flow
    This only controls the execution flow of the miner process
    '''
    def __start_mining(self):
        while self.__miner_thread_running:
            # Miner currenty paused or has no work to do
            if self.__miner_paused is True or self.__transaction_pool == []:
                continue

            else:
                # Miner not running even though its not paused
                if self.__miner_process is None \
                        or not self.__miner_process.is_alive():
                    self.__start_miner_process()
                    continue

                # Miner found a candidate
                elif not self.__miner_result_queue.empty():
                    candidate = self.__get_candidate_block()

                    # Candidate not found, retry
                    if candidate is None:
                        self.__reset_miner_process()
                        continue

                    self.__broadcast_candidate(candidate)
                    self.__blockchain.add_block(block=candidate)
                    self.__reset_miner_process(
                        candidate.get_data().get_transactions()
                    )
                    continue

    '''
    Calculate proof of work
    Return found Candidate
    '''
    def __proof_of_work(
        self
    ):
        transactions = self.__transaction_pool
        # calculate the difficulty target
        target = 2 ** (256-self.__difficulty_bits)
        start_point = randint(0, self.__max_nonce)
        end_point = start_point + self.__max_nonce

        for nonce in range(start_point, end_point):
            candidate_block = Block(
                self.__get_current_head_hash(),
                nonce,
                transactions,
                self.__blockchain.get_blockchain_head()
            )
            hash_result = candidate_block.get_hash()

            # check if this is a valid result, below the target
            if int(hash_result, 16) < target:
                self.__log.debug(f"Success with nonce {nonce}")
                self.__log.debug(f'Hash is {hash_result}')
                self.__log.debug(f"Hash previous: {self.__get_current_head_hash()}")
                self.__miner_result_queue.put(candidate_block)
                return

        self.__log.error(f'Failed after {nonce} tries')
        self.__miner_result_queue.put(None)

    def __get_current_head_hash(self):
        return self.__blockchain.get_blockchain_head().get_hash()
