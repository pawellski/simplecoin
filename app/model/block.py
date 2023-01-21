from hashlib import sha256

class Block:
    def __init__(self, previous_block_hash, nonce, transactions, previous_block):
        # first part of block which contains important information 
        self.__header = self.Header(previous_block_hash, nonce)
        # second part of block which contains transactions
        self.__data = self.Data(transactions)
        # reference to previous block
        self.__previous_block = previous_block

    def set_previous_block(self, block):
        self.__previous_block = block

    def get_previous_block(self):
        return self.__previous_block

    def get_header(self):
        return self.__header

    def get_data(self):
        return self.__data

    """
    Return block as a dictionary with two
    important keys - header and data
    """
    def to_dict(self, key_as_hex=False):
        block = {}
        block['header'] = self.__header.to_dict(key_as_hex)
        block['data'] = self.__data.to_dict(key_as_hex)
        if key_as_hex is True:
            block['header']['hash'] = self.get_hash()
        return block

    """
    Calculate and return sha256
    bases on cast dictionary to str
    """
    def get_hash(self):
        data = str(self.to_dict())
        return sha256(data.encode('utf-8')).hexdigest()


    class Header:
        def __init__(self, previous_block_hash, nonce):
            self.__previous_block_hash = previous_block_hash
            self.__nonce = nonce

        def get_previous_block_hash(self):
            return self.__previous_block_hash

        def get_nonce(self):
            return self.__nonce

        def set_previous_block_hash(self, previous_block_hash):
            self.__previous_block_hash = previous_block_hash

        def set_nonce(self, nonce):
            self.__nonce = nonce

        """
        Return header as a dictionary
        """
        def to_dict(self, key_as_hex=False):
            header = {}
            header['previous_block_hash'] = self.__previous_block_hash
            if not key_as_hex:
                header['nonce'] = self.__nonce
            return header

    class Data:
        def __init__(self, transactions):
            self.__transactions = transactions

        def set_transactions(self, transactions):
            self.__transactions = transactions

        def get_transactions(self):
            return self.__transactions

        def add_transaction(self, transaction):
            self.__transactions.append(transaction)

        def clear_transactions(self):
            self.__transactions = []

        def to_dict(self, key_as_hex=False):
            return [t.to_dict(True, key_as_hex) for t in self.__transactions]
