import os, json
from KYC_WalletApp.w3.rinkey_connection import Connection


w3 = Connection.CONNECTION

class Wallet_Factory:
    def __init__(self):
        self.ADDRESS = '0x3aec29207CDBf369F058F25FcFE762ae3a7E1299'


    def Factory(self):
        contractPath = os.path.join(os.getcwd(), 'KYC_WalletApp', 'w3', 'walletFactory')
        with open(contractPath, 'r') as c:
            data = c.read()
            factory = json.loads(data)
        return w3.eth.contract(
            address=self.ADDRESS,
            abi=factory['abi']
        )

factory = Wallet_Factory().Factory()


