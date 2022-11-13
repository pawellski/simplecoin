# simplecoin
The repository contains own implementation of a crypto-currency. This project is realized as part of Applied cryptography course at univeristy.

---

## first milestone
### assumptions:
- add new node to network
- verification of signed message by other node
### realization:
The application was implemented in flask framework (bases on python 3.10) using ecdsa and pycroptodome libraries. The main source code is *node.py* which imitates node in network. Initially, 4 nodes were created, available at the following addreses:
| node | local ip address | docker ip address |
| ----------- | ----------- | ----------- |
| node-1 | http://localhost:8081 | http://172.16.238.101:8881 |
| node-2 | http://localhost:8082 | http://172.16.238.102:8882 |
| node-3 | http://localhost:8083 | http://172.16.238.103:8883 |
| node-4 | http://localhost:8084 | http://172.16.238.104:8884 |

In order to add a new node to the network, you should send request on */connect* endpoint on local ip address of new node and give **docker ip address** of other node in json format.

In order to display public keys list, you should send request on */pub-key-list* selected node endpoint.

The second topic was verification of a signed message. You need to send a request to */send-message* endpoint and provide a json which consisting of two keys -- docker ip address (of the node which recives and verifies the message) and the message (plain text). The endpoint returns a response from the node that performed the verification.
### API:


---
## second milestone
### assumptions:
- add blockchain structure and provide storing it in a file
- add message generator which adds signed messages to transcation pool with fixed interval
- add miner that searches candidate block and propagate it
### realization:
The blockchain structure was implemented in *blockchain.py* file as linked list and bases on block class (implemented in *block.py*). Structure is responsible for adding candidate block to the blockchain, storing blockchain and reading it after start app.

The message generator was implemented in *message_generator.py* file. It generates the messages, signes them and broadcasts to other nodes in network. The default time interval, with the generation process is performed, is 5 seconds. Diffrent interval can be given in request body.   
### API:
- blockhain verification

  `GET /verify-blockchain`

- start message generator

  `POST /start-generator`
    content [optional]:
    - json format with body {"interval" : n}, where n is integer value that represents a time interval 

- stop message generator

  `POST /stop-generator`

---
## authors
- Bieńkowski Mikołaj
- Kuczka Łukasz
- Skiba Paweł
