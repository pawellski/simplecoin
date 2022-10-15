from uuid import uuid4
import requests
import json
from os import environ

class KeyHandler:
    def __init__(self):
        self.pub_key_list = {}
        self.pub_key_list['entries'] = []
        self.pub_key = None
        self.priv_key = None
        self.ip = f"http://{environ['NODE_IP']}"
        self.create_key_pair()
        
    def fetch_curr_ip(self):
        return json.loads(requests.get("https://ip.seeip.org/jsonip?").text)["ip"]
    
    def get_curr_ip(self):
        return self.ip
    
    def create_key_pair(self):
        if self.priv_key is None and self.pub_key is None:     
            self.priv_key = str(uuid4())
            self.pub_key = str(uuid4())
    
    def get_private_key(self):
        return self.priv_key
    
    def get_public_key(self):
        return self.pub_key
    
    def update_pub_key_list(self, new_pub_key_list):
        self.pub_key_list = new_pub_key_list
    
    def save_new_pub_key(self, new_entry):
        for el in self.pub_key_list['entries']:
        
            if el == new_entry:
                return
        
            if el['ip'] == new_entry['ip']:
                el['pub_key'] = new_entry['pub_key']
                return
        
        self.pub_key_list['entries'].append(new_entry)
        
    def get_pub_key_list(self):
        return self.pub_key_list
        
    
    