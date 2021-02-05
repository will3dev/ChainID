from web3 import Web3
from KYC_WalletApp.w3.ganache_connection import Connection as g3
from KYC_WalletApp.w3 import Connection as r3

from Database.user_sql import *

ganache = g3.CONNECTION
rinkeby = r3.CONNECTION

def create_account(w3, username, password):
    '''
    This will be used to generate a new account for a user.
    This would store the encrypted account object in the DB.
    User would need to retain the PW.
    Will return account public address
    :param w3:
    :param username:
    :param password:
    :return:
    '''
    create_users_table()
    account = w3.eth.account.create()
    address = account.address
    keystore = account.encrypt(password)
    add_user = new_user(username, keystore, address)
    if not add_user:
        return 0
    return address

def create_transaction(value, from_address, w3):
    if value > 0:
        transaction = {
            'chainID': 4,
            'from': from_address,
            'value': value,
            'nonce': w3.eth.getTransactionCount(from_address)
        }
    else:
        transaction = {
            'chainID': 4,
            'from': from_address,
            'nonce': w3.eth.getTransactionCount(from_address)
        }
    return transaction

def sign_transaction(w3, transaction, username, password):
    '''
    Would need to look up user decrypt the keystore.
    Then return signed transaction object.

    :param transaction:
    :param username:
    :param password:
    :return:
    '''

    # account.privateKey.hex()
    data = get_userData(username)
    ks = data.get('keystore')
    pk = w3.eth.account.decrypt(ks, password).hex()
    account = w3.eth.account.privateKeyToAccount(pk)
    return account.signTransaction(transaction)

def get_balance(w3, username):
    '''
    This would query teh DB and get the users account address.
    Then get the balance over the connection for that
    :param username:
    :return: value in ether
    '''

    data = get_userData(username)
    address = data.get('address')
    return  Web3.fromWei(w3.eth.getBalance(address), 'ether')

