from web3 import Web3

class Connection:
    GANACHE_URL = 'HTTP://127.0.0.1:7545'
    CONNECTION = Web3(Web3.HTTPProvider(GANACHE_URL))