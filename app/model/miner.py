from logging import Logger
from multiprocessing import Process, Queue
from threading import Thread
from random import randint
from time import time
from requests import post
from model.transaction import Transaction
from model.transaction_tuples import OutputTuple
from model.wallet import Wallet
from model.block import Block
from model.blockchain import Blockchain
from model.key_manager import KeyManager


class Miner:
    def __init__(
        self,
        log: Logger,
        difficulty_bits: int,
        blockchain: Blockchain,
        key_manager: KeyManager,
        wallet: Wallet,
        worker_income: int
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
        self.__wallet = wallet
        self.__worker_income = worker_income

    def append_transaction(
        self,
        transaction_dict: dict
    ):
        self.__log.debug("Appending trasaction")
        try:
            transaction = Transaction.from_dict_to_transaction(
                transaction_dict
            )
            self.__transaction_pool.append(transaction)
            self.__log.info('Transaction appended successfuly')
        except Exception as e:
            self.__log.error(f'Error appending transaction: {e}')
        return "Transaction appended"

    '''
    Initialization of addition a new candidate to blockchain/orphan list
    '''
    def init_addition_of_candidate(self, block_dict):
        self.__stop_miner_process()
        self.__filter_transaction_pool(block_dict)

    '''
    Filtration transaction pool - removing from transaction pool transactions that are in new block
    '''
    def __filter_transaction_pool(self, block_dict):
        transactions_from_new_candidate=[Transaction.from_dict_to_transaction(t) for t in block_dict['data']],
        self.__transaction_pool = [transaction for transaction in self.__transaction_pool if not transaction in transactions_from_new_candidate]

    '''
    Update head block after new candidate gets appended
    '''
    def reset_miner_after_new_candidate_request(self, is_orphan):
        if not is_orphan:
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
                            f"Error sending candidate to node {el['ip']}"
                            f"error: {res.content}"
                        )
                except Exception as e:
                    self.__log.error(
                        f"Error sending candidate to node {el['ip']}, "
                        f"error: {e}"
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
            "Starting miner process"
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
                    pending_transactions = self.__transaction_pool 
                    self.__start_miner_process()
                    continue

                # Miner found a candidate
                elif not self.__miner_result_queue.empty():
                    candidate = self.__get_candidate_block()

                    # Candidate not found, retry
                    if candidate is None:
                        self.__reset_miner_process()
                        continue

                    # Transaction list after filtering is empty
                    if candidate is False:
                        self.__reset_miner_process(pending_transactions)
                        continue

                    self.__broadcast_candidate(candidate)
                    self.__blockchain.add_block(candidate)
                    self.__reset_miner_process(
                        candidate.get_data().get_transactions()
                    )
                    continue

    '''
    Check if transaction id is unique - go through whole blockchain
    '''
    def __check_transaction_id(self, transaction: Transaction):
        current_block = self.__blockchain.get_blockchain_head()
        while current_block is not None:
            block_transactions = current_block.get_data().get_transactions()
            for block_transaction in block_transactions:
                if block_transaction.get_id() == transaction.get_id():
                    self.__log.error("Transaction ID not unique")
                    return False
            current_block = current_block.get_previous_block()
        return True

    '''
    Check if inputs are unspent
    '''
    def __check_inputs_unspent(
        self,
        transaction: Transaction,
        previous_inputs: list
    ):
        if len(transaction.get_inputs()) == 0:
            self.__log.error(f"Error - empty list for transaction "
                             f"{transaction.get_id()}")
            return False

        transaction_pub_key = transaction.get_output().get_current_owner()
        unspent_outputs = self.__wallet.get_unspent_outputs(
            transaction_pub_key
        )
        for input in transaction.get_inputs():
            if (
                input.get_previous_id() in
                    [i.get_previous_id() for i in 
                     previous_inputs.get(transaction_pub_key, [])]
            ):
                self.__log.error(
                    f"Input with id {input.get_previous_id()} "
                    f"has already been spent in previous mined transactions"
                )
                return False
            if (
                input.get_previous_id() not in unspent_outputs.keys()
            ):
                self.__log.error(
                    f"Input with id {input.get_previous_id()} "
                    f"has already been spent in previous block "
                    f"{input.get_amount()}"
                )
                return False
        return True

    '''
    Check if inputs amount matches outputs + fee
    '''
    def __check_inputs_value(self, transaction: Transaction):
        total_amount = 0
        for input in transaction.get_inputs():
            total_amount += input.get_amount()
        total_amount = round(total_amount, 3)

        # output + change + fee
        expected_amount = round(
            transaction.get_output().get_current_amount() +
            transaction.get_fee() +
            transaction.get_output().get_new_amount(),
            3
        )

        if expected_amount != total_amount:
            self.__log.error(
                f"Inputs amount {total_amount} " 
                f"does not match expected amount {expected_amount}")
            return False
        return True

    '''
    Check if transaction signature is correct
    '''
    def __check_transaction_signature(self, transaction: Transaction):
        sender_pub_key = transaction.get_inputs()[0].get_current_owner()
        return self.__key_manager.verify_signature(
            sender_pub_key,
            transaction.get_signature(),
            transaction.get_hash()
        )

    '''
    Verify transactions processed by the miner
    1. Check if transaction id is unique
    2. Check if inputs are unspent
    3. Check if inputs cover outputs + fee
    4. Verify signatures
    5. Verify if there are no issues with amount mismatch output/input
    '''
    def __get_valid_transactions(self, pending_transactions):
        valid_transactions = []
        previous_inputs = {}
        for transaction in pending_transactions:
            sender_pub_key = transaction.get_output().get_current_owner()
            if (
                self.__check_transaction_id(transaction) and
                self.__check_inputs_unspent(transaction, previous_inputs) and
                self.__check_inputs_value(transaction) and
                self.__check_transaction_signature(transaction)
            ):
                for input in transaction.get_inputs():
                    if sender_pub_key not in previous_inputs.keys():
                        previous_inputs[sender_pub_key] = []
                    previous_inputs[sender_pub_key].append(input)
                valid_transactions.append(transaction)
            else:
                pending_transactions.remove(transaction)
        return valid_transactions

    def __create_coinbase_transaction(self, valid_transactions):
        total_amount = self.__worker_income
        for transaction in valid_transactions:
            total_amount += transaction.get_fee()
        total_amount = round(total_amount, 3)
        return self.__wallet.makeup_transaction(
            is_coinbase=True,
            output=OutputTuple(
                self.__key_manager.get_pub_key_str(),
                self.__key_manager.get_pub_key_str(),
                total_amount,
                0
            ),
            fee=0
        )

    def __prepare_transactions(self):
        start = time()
        pending_transactions = self.__transaction_pool
        valid_transactions = self.__get_valid_transactions(
            pending_transactions
        )
        if len(valid_transactions) > 0:
            valid_transactions.append(
                self.__create_coinbase_transaction(
                    valid_transactions
                )
            )
        diff = start - time()
        self.__log.info(
            f'Transactions filtered in {diff}s, '
            f'lenght: {len(valid_transactions)}'
        )
        return valid_transactions

    '''
    Calculate proof of work
    Return found Candidate
    '''
    def __proof_of_work(
        self
    ):
        # Verify transactions
        transactions = self.__prepare_transactions()
        self.__log.info(f'Filtered transaction list len: {len(transactions)}')
        # calculate the difficulty target
        target = 2 ** (256-self.__difficulty_bits)

        if len(transactions) == 0:
            self.__log.error('Filtered transaction list is empty')
            self.__miner_result_queue.put(False)
            return

        start = time()
        for nonce in range(0, self.__max_nonce):
            candidate_block = Block(
                self.__get_current_head_hash(),
                nonce,
                transactions,
                self.__blockchain.get_blockchain_head()
            )
            hash_result = candidate_block.get_hash()

            # check if this is a valid result, below the target
            if int(hash_result, 16) < target:
                end = time() - start
                self.__log.debug(f"Success with nonce {nonce} in time {end}s")
                self.__log.debug(f'Hash is {hash_result}')
                self.__log.debug(
                    f"Hash previous: {self.__get_current_head_hash()}"
                )
                self.__miner_result_queue.put(candidate_block)
                return

        self.__log.error(f'Failed after {nonce} tries')
        self.__miner_result_queue.put(None)

    def __get_current_head_hash(self):
        return self.__blockchain.get_blockchain_head().get_hash()

    def proof_of_work(
        self,
        transactions
    ):

        # calculate the difficulty target
        target = 2 ** (256-self.__difficulty_bits)
        start_point = randint(0, self.__max_nonce)
        end_point = start_point + self.__max_nonce

        for nonce in range(start_point, end_point):
            candidate_block = Block(
                None,
                nonce,
                transactions,
                self.__blockchain.get_blockchain_head()
            )
            hash_result = candidate_block.get_hash()

            # check if this is a valid result, below the target
            if int(hash_result, 16) < target:
                self.__log.debug(f"Success with nonce {nonce}")
                return candidate_block

        self.__log.error(f'Failed after {nonce} tries')
        self.__miner_result_queue.put(None)