import os
import json
from KYC_WalletApp.w3.rinkey_connection import Connection


w3 = Connection.CONNECTION

class Wallet_Contract:
    def Wallet(self, original_address):
        address = w3.toChecksumAddress(original_address.rstrip())
        contractPath = os.path.join(os.getcwd(), 'KYC_WalletApp', 'w3', 'walletContract')
        with open(contractPath, 'r') as c:
            data = c.read()
            factory = json.loads(data)
        return w3.eth.contract(
            address=address,
            abi=factory['abi']
        )