import base64, json
from requests import post
from os import environ
import base64, json
from flask import jsonify
import logging
import random
import threading
import time


DEFAULT_INTERVAL = 5
class MessageGenerator():
    def __init__(self, log, key_manager):
        self.__generator_thread = None
        self.__log = log
        self.__key_manager = key_manager   
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
    Generate message and broadcast it to others in appropriate interval
    Set the __generator_active flag on True and call two methods in while loop with time break
    If __generator_active flag is False than leave the loop
    """
    def generation_process(self, INTERVAL):
        self.__generator_active = True
        while self.__generator_active:
            message, signed_message = self.__generate_new_message()
            self.__broadcast_transaction_message(message, signed_message)
            time.sleep(INTERVAL)

    """
    Create and sign new message
    """
    def __generate_new_message(self):
        message = "message"+str(random.randint(0,1000))
        signed_message = self.__key_manager.sign_message(message)
        self.__log.info(f"Sucessfully generated and signed new transaction message")
        return message, signed_message
    
    """
    Broadcast plaintext and signed_message to others
    Call method to make requests
    """
    def __broadcast_transaction_message(self, message, signed_message):         
        body = { "signed_message": base64.b64encode(signed_message).decode('utf-8'),
                 "message":message
         }

        result, ip = self.__requests_transaction_message_broadcast(body)
        if not result:
            raise Exception(f"Error broadcasting transaction message to {ip}")    
        else:
            self.__log.info(f"Successfully broadcasted transaction message")

    """
    In foreach loop, calling method to make request to every ip that is in pub_key_list
    """
    def __requests_transaction_message_broadcast(self, request_data):
        self.__log.info(f"Starting process for broadcasting transaction message")

        for el in self.__key_manager.get_pub_key_list()['entries']:
            res = self.__request_transaction_message_broadcast(el['ip'], request_data)
            if not res:
                self.__log.info(f"Transaction message broadcast process failed")
                return False, el['ip']
        return True, None

    """
    Make request to endpoint /update-transaction-pool for concrete node,
    with plaintext and signed message as a body
    """
    def __request_transaction_message_broadcast(self, ip, request_data):
        self.__log.info(f"Requesting transaction message broadcast for ip {ip}")
        try:
            res = post(self.__key_manager.format_ip(ip, '/update-transaction-pool'), json = request_data)
            return True if res.ok else False
        except Exception as e:
            self.__log.error(f"Transaction message broadcast for ip {ip} failed, reason: {e}")
            return False