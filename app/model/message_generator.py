import base64, json
from decimal import Decimal
from requests import post
from os import environ
import base64, json
from flask import jsonify
import logging
import random
import threading
import time
from model.transaction_tuples import OutputTuple

DEFAULT_INTERVAL = 5
FEE = 0.002
class MessageGenerator():
    def __init__(self, log, key_manager, wallet):
        self.__generator_thread = None
        self.__log = log
        self.__key_manager = key_manager 
        self.__wallet = wallet  
        self.__generator_active = False
          
    """
    Start generator by requesting to endpoint /start-generator
    Create a new thread to manage generation process
    If there isn't a interval value in body, use default interval
    If requested interval is not an integer raise an error 
    """
    def start_generator(self, request):
        if request.is_json:
            request_data = request.json
            if(isinstance(request_data["interval"], int)):
                INTERVAL = request_data["interval"]
                self.__log.info(f"Generation using requested interval: {INTERVAL}s")
            else:
                error_message = (f"Requested interval type, should be an integer instead of {type(request_data['interval'])}")
                self.__log.error(error_message)
                raise Exception(error_message)
        else:
            INTERVAL = DEFAULT_INTERVAL  
            self.__log.info(f"Generation using default interval: {INTERVAL}s")
          
        self.__log.info(f"Message Generator is started")
        self.__generator_thread = threading.Thread(target=self.generation_process, args=[INTERVAL])
        self.__generator_thread.start()
        return "Message Generator is started"

    """
    Stop generator by requesting to endpoint /stop-generator
    Change value of __generator_active flag to False
    """    
    def stop_generator(self):
        self.__log.info(f"Message Generator is stopped")
        if (self.__generator_active):
            self.__generator_active = False
        return "Message Generator is stopped"  

    """
    Generate transaction and broadcast it to others in appropriate interval
    Set the __generator_active flag on True and call two methods in while loop with time break
    If __generator_active flag is False than leave the loop
    """
    def generation_process(self, INTERVAL):
        self.__generator_active = True
        while self.__generator_active:
            transaction = self.__generate_transaction()
            self.__broadcast_transaction(transaction)
            time.sleep(INTERVAL)

    """ 
    Broadcast ganerated transaction to others
    Call method to make requests
    """
    def __broadcast_transaction(self, transaction):    

        body = transaction.to_dict(True) 

        result, ip = self.__requests_transaction_broadcast(body)
        if not result:
            self.__log.error(f"Error broadcasting transaction to {ip} - empty result")
        else:
            self.__log.info(f"Successfully broadcasted transaction")

    """
    In foreach loop, calling method to make request to every ip that is in pub_key_list
    """
    def __requests_transaction_broadcast(self, request_data):
        self.__log.info(f"Starting process for broadcasting transaction")

        for el in self.__key_manager.get_pub_key_list()['entries']:
            res = self.__request_transaction_broadcast(el['ip'], request_data)
            if not res:
                return False, el['ip']
        return True, None

    """
    Make request to endpoint /update-transaction-pool for concrete node,
    with transaction as a body
    """
    def __request_transaction_broadcast(self, ip, request_data):
        self.__log.info(f"Requesting transaction broadcast for ip {ip}")
        try:
            res = post(self.__key_manager.format_ip(ip, '/update-transaction-pool'), json = request_data)
            return True if res.ok else False
        except Exception as e:
            self.__log.error(f"Transaction broadcast for ip {ip} failed, reason: {e}")
            return False

    """
    Check balance of the account
    Create output -  read current owner, pick addressee and amount to transfer, calculate the change 
    Create new transaction
    """
    def __generate_transaction(self):
        pub_key_list = [entry['pub_key'] for entry in self.__key_manager.get_pub_key_list()['entries'] if entry['pub_key'] != self.__key_manager.get_pub_key_str()]
        is_coinbase = False
        try:
            balance = self.__wallet.check_balance()
            new_amount = round(random.uniform(0, balance - FEE), 3)
            output = OutputTuple (
                        random.choice(pub_key_list),
                        self.__key_manager.get_pub_key().decode('utf-8'),
                        new_amount,
                        round(balance - new_amount - FEE, 3)
                    )
            transaction = self.__wallet.makeup_transaction(is_coinbase, output, FEE)
            self.__log.info(f"Sucessfully generated new transaction")
            return transaction
        except Exception as e:
            self.__log.error(f"Transaction generation failed, reason: {e}")
            return None