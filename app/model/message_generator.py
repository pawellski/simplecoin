import base64, json
from requests import post
from os import environ
import base64, json
from flask import jsonify
import logging
import random
import threading
import time

class MessageGenerator:
    def __init__(self, log, key_manager):
        self.__generator_thread = None
        self.__log = log
        self.__key_manager = key_manager
        self.__INTERVAL = 5.0
        self.__is_generator_started = False

    def start_generator(self):
        self.__generator_thread = threading.Timer(self.__INTERVAL, self.generation_process)
        self.__generator_thread.start()
        self.__is_generator_started = True
        self.__log.info(f"Message Generator is started")
        return "Message Generator is started"

    def stop_generator(self):
        if (self.__is_generator_started):
            self.__generator_thread.cancel()
            self.__is_generator_started = False
            self.__log.info(f"Message Generator is stopped")
        return "Message Generator is stopped"        

    def generation_process(self):
        message = self.__generate_new_message()
        self.__broadcast_transaction_message(message)

    def __generate_new_message(self):
        message = "message"+str(random.randint(0,1000))
        signed_message = self.__key_manager.sign_message(message)
        self.__log.info(f"Sucessfully generated and signed new transaction message")
        return signed_message
    
    def __broadcast_transaction_message(self, transaction_message):   
        body = { "signed_message": base64.b64encode(transaction_message).decode('utf-8') }

        result, ip = self.__requests_transaction_message_broadcast(body)
        if not result:
            raise Exception(f"Error broadcasting transaction message to {ip}")    
        else:
            self.__log.info(f"Successfully broadcasted transaction message")

    def __requests_transaction_message_broadcast(self, request_data):
            self.__log.info(f"Starting process for broadcasting transaction message")

            for el in self.__key_manager.get_pub_key_list()['entries']:
                res = self.__request_transaction_message_broadcast(el['ip'], request_data)
                if not res:
                    self.__log.info(f"Transaction message broadcast process failed")
                    return False, el['ip']
            return True, None

    def __request_transaction_message_broadcast(self, ip, request_data):
        self.__log.info(f"Requesting transaction message broadcast for ip {ip}")
        try:
            res = post(self.__key_manager.format_ip(ip, '/update-transaction-pool'), json = request_data)
            return True if res.ok else False
        except Exception as e:
            self.__log.error(f"Transaction message broadcast for ip {ip} failed, reason: {e}")
            return False
    

 

     
