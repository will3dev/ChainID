import json
from web3 import Web3
from KYC_WalletApp.w3.rinkey_connection import Connection as r3


rinkeby = r3.CONNECTION


def create_account(password, w3=rinkeby):
    account = w3.eth.account.create()
    address = account.address
    keystore = account.encrypt(password)
    return {'address': address, 'keystore': keystore}


def get_account_balance(address, w3=rinkeby):
    bal = w3.eth.getBalance(address)
    return w3.fromWei(bal, 'ether')


def transfer_ether(value, to_account, from_account, w3=rinkeby):
    # the user value should pass the DB user result

    transaction = {
        'from': from_account.address,
        'to': to_account,
        'value': Web3.toWei(value, 'ether'),
        'nonce': w3.eth.getTransactionCount(from_account.address),
        'gasPrice': w3.eth.gasPrice,
        'gas': 1000000
    }
    signed_txn = from_account.sign_transaction(transaction)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return w3.eth.waitForTransactionReceipt(txn_hash)


