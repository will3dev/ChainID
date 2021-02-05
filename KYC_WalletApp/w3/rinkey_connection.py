from web3 import Web3

class Connection:
    RINKEBY_URL = 'https://rinkeby.infura.io/v3/328d6f459b0341afb9d3f8b43f758234'
    CONNECTION = Web3(Web3.HTTPProvider(RINKEBY_URL))

w3 = Connection().CONNECTION