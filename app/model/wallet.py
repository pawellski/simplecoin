from model.block import Block
from model.blockchain import Blockchain
from model.key_manager import KeyManager
from model.transaction import Transaction
from model.transaction_tuples import InputTuple

class Wallet:
    def __init__(self, key_manager, blockchain, log):
        self.__log = log
        self.__key_manager = key_manager
        self.__blockchain = blockchain

    def __get_output_transactions(self):
        transactions = {}
        block = self.__blockchain.get_blockchain_head()
        while block is not None:
            for t in block.get_data().get_tranactions():
                outputs = (t.get_output().get_new_owner(), t.get_output().get_current_owner_change())
                if self.__key_manager.get_pub_key() in outputs:
                    transactions[t.get_id()] = t
            block = block.get_previous_block()
        return transactions

    def __remove_input_transactions(self, transactions):
        block = self.__blockchain.get_blockchain_head()
        while block is not None:
            for t in block.get_data().get_tranactions():
                for i in t.get_inputs(): 
                    if i.get_previous_id() in transactions.keys():
                        del transactions[i.get_previous_id()]
            block = block.get_previous_block()

    def __get_unspent_outputs(self):
        unspent_outputs = {}
        transactions = self.__get_output_transactions()
        self.__remove_input_transactions(transactions)
        for t in transactions.values():
            if t.get_output().get_new_owner() == self.__key_manager.get_pub_key():
                unspent_outputs[t.get_id()] = t.get_output().new_amount()
            elif t.get_output().get_current_owner() == self.__key_manager.get_pub_key():
                unspent_outputs[t.get_id()] = t.get_output().current_amount()
        return unspent_outputs

    def check_balance(self):
        unspent_outputs = self.__get_unspent_outputs()
        balance = 0.0
        for amount in unspent_outputs.values():
            balance += amount
        return balance

    def makeup_transaction(self, is_coinbase, output, fee):
        unspent_outputs = self.__get_unspent_outputs()
        inputs = []
        for transaction_id, amount in unspent_outputs.items():
            inputs.append(InputTuple(transaction_id, self.__key_manager.get_pub_key(), amount))
        transaction = Transaction(is_coinbase, inputs, output, fee)
        signature = self.__key_manager.sign_message(transaction.to_dict())
        transaction.set_signature(signature)
        return transaction
