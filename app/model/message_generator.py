import base64, json
from requests import post
from os import environ
import base64, json
from flask import jsonify
import logging

class MessageGenerator:
    def __init__(self, log, ip):
        self.__log = log
        self.__ip = ip

    def generate_new_message(self):
        message = "message1"

        body = { "message": message }

        try:
            res = post(self.__format_ip(self.__ip, '/sign-transaction-message'), json = body)
            if res.ok:
                self.__log.info(f"Sucessfully signed transaction message, received {res.content}")
                return res.content
            else:
                raise Exception("Error sending transaction message to sign")
        except Exception as e:
            e.message = f"Error encountered during call to signing transaction message, error: {e}"
            raise

    def __format_ip(self, ip, endpoint):
        return f"{ip}/{endpoint}"

     
