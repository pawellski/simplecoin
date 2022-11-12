class Miner:
    def __init__(self, log):
        self.__log = log

    def update_transaction_pool(self, request_data):
        message = request_data["message"]
        signed_message = request_data["signed_message"]
        self.__log.info(f"!!!!!!!!!  TRANSACTION POOL UPDATED   !!!!!!!!!   plaintext = {message} , signed = {signed_message}")
        return "Success"