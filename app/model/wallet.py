import base64
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

    """
    Iterate through the entire blockchain and every transaction
    Return transactions list which contains output for given pub_key or self
    """
    def __get_output_transactions(self, pub_key):
        if pub_key is None:
            pub_key = self.__key_manager.get_pub_key_str()
        transactions = {}
        block = self.__blockchain.get_blockchain_head()
        while block is not None:
            for t in block.get_data().get_transactions():
                outputs = (t.get_output().get_new_owner(), t.get_output().get_current_owner())
                if pub_key in outputs:
                    transactions[t.get_id()] = t
            block = block.get_previous_block()
        return transactions

    """
    Remove transactions from list which exists in input
    """
    def __remove_input_transactions(self, transactions, pub_key):
        block = self.__blockchain.get_blockchain_head()
        while block is not None:
            for t in block.get_data().get_transactions():
                for i in t.get_inputs(): 
                    if i.get_previous_id() in transactions.keys() and pub_key == i.get_current_owner():
                        del transactions[i.get_previous_id()]
            block = block.get_previous_block()

    """
    Return unspent outputs for given public key
    or collect own unspent outputs
    """
    def get_unspent_outputs(self, pub_key=None):
        if pub_key is None:
            pub_key = self.__key_manager.get_pub_key_str()
        unspent_outputs = {}
        transactions = self.__get_output_transactions(pub_key)
        self.__remove_input_transactions(transactions, pub_key)
        for t in transactions.values():
            if t.get_output().get_new_owner() == pub_key and t.get_output().get_new_amount() > 0:
                unspent_outputs[t.get_id()] = t.get_output().get_new_amount()
            elif t.get_output().get_current_owner() == pub_key and t.get_output().get_current_amount() > 0:
                unspent_outputs[t.get_id()] = t.get_output().get_current_amount()
        return unspent_outputs

    """
    Return own current balance
    """
    def check_balance(self, pub_key=None):
        unspent_outputs = self.get_unspent_outputs(pub_key)
        balance = 0.0
        for amount in unspent_outputs.values():
            balance += amount
        return balance

    """
    Create new transaction, sign and return it
    """
    def makeup_transaction(self, is_coinbase, output, fee):
        inputs = []
        if not is_coinbase:
            unspent_outputs = self.get_unspent_outputs()
            for transaction_id, amount in unspent_outputs.items():
                inputs.append(InputTuple(transaction_id, self.__key_manager.get_pub_key_str(), amount))
        transaction = Transaction(is_coinbase, inputs, output, fee)
        signature = self.__key_manager.sign_message(str(transaction.get_hash()))
        transaction.set_signature(base64.b64encode(signature).decode('utf-8'))
        return transaction