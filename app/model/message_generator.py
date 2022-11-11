import base64, json
from requests import post
from os import environ
import base64, json
from flask import jsonify
import logging
import random
import threading
import time

class MessageGenerator(threading.Thread):
    def __init__(self, log, key_manager):
        self.__generator_thread = None
        self.__log = log
        self.__key_manager = key_manager
        self.__INTERVAL = 5
        self.__ON_OFF_generator = False

    def start_generator(self):
        self.__log.info(f"Message Generator is started")
        self.__generator_thread = threading.Thread(target=self.generation_process)
        self.__generator_thread.run()
        return "Message Generator is started"
        
    def stop_generator(self):
        if (self.__ON_OFF_generator):
            self.__ON_OFF_generator = False
            self.__log.info(f"Message Generator is stopped")
        return "Message Generator is stopped"        

    def generation_process(self):
        self.__ON_OFF_generator = True
        while self.__ON_OFF_generator:
            message, signed_message = self.__generate_new_message()
            self.__broadcast_transaction_message(message, signed_message)
            time.sleep(self.__INTERVAL)

    def __generate_new_message(self):
        message = "message"+str(random.randint(0,1000))
        signed_message = self.__key_manager.sign_message(message)
        self.__log.info(f"Sucessfully generated and signed new transaction message")
        return message, signed_message
    
    def __broadcast_transaction_message(self, message, signed_message):   
        
        body = { "signed_message": base64.b64encode(signed_message).decode('utf-8'),
                 "message":message
         }

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
    

 

     
