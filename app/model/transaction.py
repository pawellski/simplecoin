from hashlib import sha256
import uuid

class Transaction:
    def __init__(self, is_coinbase, addressee, amount_out, sender, amount_change, fee):
        self.__id = uuid.uuid4()
        self.__is_coinbase = is_coinbase
        self.__inputs = []
        self.__output = self.Output(sender, addressee, amount_out, amount_change)
        self.__fee = fee

    def __get_inputs_to_dict(self):
        inputs = []
        for i in self.__inputs:
            inputs.append(i.to_dict())
        return inputs

    def get_inputs(self):
        return self.__inputs

    def get_output(self):
        return self.__output

    def get_id(self):
        return self.__id

    def to_dict(self):
        transaction = {}
        transaction['id'] = self.__id
        transaction['is_coinbase'] = self.__is_coinbase
        transaction['inputs'] = self.__get_inputs_to_dict()
        transaction['output'] = self.__output.to_dict()
        transaction['fee'] = self.__fee
        return transaction

    def get_hash(self):
        transaction = str(self.to_dict())
        return sha256(transaction.encode('utf-8')).hexdigest()

    def add_input(self, previous_id, sender, amount_in):
        self.__inputs.append(self.Input(previous_id, sender, amount_in))


    class Output:
        def __init__(self, sender, addressee, amount_out, amount_change):
            self.__sender = sender
            self.__addressee = addressee
            self.__amount_out = amount_out
            self.__amount_change = amount_change

        def to_dict(self):
            output = {}
            output['sender'] = self.__sender
            output['addressee'] = self.__addressee
            output['amount_out'] = self.__amount_out
            output['amount_change'] = self.__amount_change
            return output

        def get_sender(self):
            return self.__sender

        def get_addressee(self):
            return self.__addressee

        def get_amount_out(self):
            return self.__amount_out

        def get_amount_change(self):
            return self.__amount_change


    class Input:
        def __init__(self, previous_id, sender, amount_in):
            self.__previous_id = previous_id
            self.__sender = sender
            self.__amount_in = amount_in

        def to_dict(self):
            input = {}
            input['previous_id'] = self.__previous_id
            input['sender'] = self.__sender
            input['amount_in'] = self.__amount_in
            return input