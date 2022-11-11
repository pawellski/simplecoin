class Miner:
    def __init__(self, log):
        self.__log = log


    def update_transaction_pool(self, request_data):
        self.__log.info(f"!!!!!!!!!  TRANSACTION POOL UPDATED   !!!!!!!!!")
        return "Success"