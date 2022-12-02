from hashlib import sha256
import uuid

from model.transaction_tuples import OutputTuple

class Transaction:
    def from_dict_to_transaction(dict):
        new_owner = dict['output']['new_owner']
        current_change = dict['output']['current_amount']
        new_amount = dict['output']['new_amount']
        current_amount = dict['output']['current_amount']
        output = OutputTuple(new_owner, current_change, new_amount, current_amount)
        transaction = Transaction(dict['is_coinbase'], dict['inputs'], output, dict['fee'], id=dict['id'])
        transaction.set_signature(dict['signature'])
        return transaction

    def __init__(self, is_coinbase, inputs, output, fee, id=None):
        if id is None:
            self.__id = str(uuid.uuid4())
        else:
            self.__id = id
        self.__is_coinbase = is_coinbase
        if self.__is_coinbase is True:
            self.__inputs = []
        else:
            self.__inputs = []
            self.__read_inputs(inputs)
        self.__output = self.Output(output.new_owner, output.current_owner_change, output.new_amount, output.current_amount)
        self.__fee = fee
        self.__signature = None

    def __read_inputs(self, inputs):
        for i in inputs:
            self.__inputs.append(self.Input(i.previous_id, i.current_owner, i.amount))

    def __get_inputs_to_dict(self):
        if self.__inputs is None:
            return []
        inputs = []
        for i in self.__inputs:
            inputs.append(i.to_dict())
        return inputs

    def get_id(self):
        return self.__id

    def get_inputs(self):
        return self.__inputs

    def get_output(self):
        return self.__output

    def get_fee(self):
        return self.__fee

    def set_signature(self, signature):
        self.__signature = signature

    def get_signature(self):
        return self.__signature

    def get_hash(self):
        transaction = str(self.to_dict())
        return sha256(transaction.encode('utf-8')).hexdigest()

    def to_dict(self, include_signature=False):
        transaction = {}
        transaction['id'] = self.__id
        transaction['is_coinbase'] = self.__is_coinbase
        transaction['inputs'] = self.__get_inputs_to_dict()
        transaction['output'] = self.__output.to_dict()
        transaction['fee'] = self.__fee
        if include_signature is True:
            transaction['signature'] = self.__signature
        return transaction


    class Output:
        def __init__(self, new_owner, current_owner_change_pub_key, new_amount, current_amount):
            self.__new_owner = new_owner
            self.__current_owner_change_pub_key = current_owner_change_pub_key
            self.__new_amount = new_amount
            self.__current_amount = current_amount

        def to_dict(self):
            output = {}
            output['new_owner'] = self.__new_owner
            output['current_owner_change_pub_key'] = self.__current_owner_change_pub_key
            output['new_amount'] = self.__new_amount
            output['current_amount'] = self.__current_amount
            return output

        def get_new_owner(self):
            return self.__new_owner

        def get_current_owner_change_pub_key(self):
            return self.__current_owner_change_pub_key

        def get_new_amount(self):
            return self.__new_amount

        def get_current_amount(self):
            return self.__current_amount


    class Input:
        def __init__(self, previous_id, current_owner, amount):
            self.__previous_id = previous_id
            self.__current_owner = current_owner
            self.__amount = amount

        def to_dict(self):
            input = {}
            input['previous_id'] = self.__previous_id
            input['current_owner'] = self.__current_owner
            input['amount'] = self.__amount
            return input

        def get_previous_id(self):
            return self.__previous_id

        def get_current_owner(self):
            return self.__current_owner

        def get_amount(self):
            return self.__amount
