from requests import post
from sys import argv
from json import dumps

new_node = "http://127.0.0.1"
new_ports = [8081, 8082, 8083, 8084]
connection_node = "http://172.16.238.10"
connection_ports = [8881, 8882, 8883, 8884]

if __name__ == "__main__":
    
    for id in range(1, 4):
        next_id = (id)%4+1
        new_node_ip = f"{new_node}:808{next_id}"
        connection_node_ip = f"{connection_node}{id}:888{id}"
         
        print(f"Connecting node-{next_id} to network hosted on node-{id}")
        res = post(f"{new_node_ip}/connect", json={"ip": f"{connection_node_ip}"})
        print(f"Returned from node-{next_id}:")
        if res.content is not None:
            print(dumps(res.json(), indent=4))