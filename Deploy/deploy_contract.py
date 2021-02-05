import os, json
from solcx import compile_source
from web3 import Web3
from web3.middleware import geth_poa_middleware
from KYC_WalletApp import create_app, db
from KYC_WalletApp.models.models import *
from eth_account import Account




rinkeby = 'https://rinkeby.infura.io/v3/328d6f459b0341afb9d3f8b43f758234'
w3 = Web3(Web3.HTTPProvider(rinkeby))


def compiled_factory():
    contractPath = os.path.join(os.getcwd(), '..', 'KYC_WalletApp', 'w3', 'walletFactory')

    with open(contractPath, 'r') as c:
        data = c.read()
        compiled_contract = json.loads(data)

    return compiled_contract


def compiled_wallet():
    contractPath = os.path.join(os.getcwd(), '..', 'KYC_WalletApp', 'w3', 'walletContract')

    with open(contractPath, 'r') as c:
        data = c.read()
        compiled_contract = json.loads(data)

    return compiled_contract


def get_user():
    app = create_app()
    app.app_context().push()
    return User.query.filter_by(username='will waltrip').first()


def get_account():
    user = get_user()
    ks = json.loads(user.keystore)
    pk = w3.eth.account.decrypt(ks, '').hex()
    return Account.from_key(pk)


def factory_contract(compiled_contract, user):
    account = get_account()

    WalletFactoryContract = w3.eth.contract(
        abi=compiled_contract['abi'],
        bytecode=compiled_contract['bin']
    )

    transaction = WalletFactoryContract.constructor(
        Web3.toWei(.25, 'ether'),
        Web3.toWei(.15, 'ether')
    ).buildTransaction()

    transaction['nonce'] = w3.eth.getTransactionCount(account.address)
    transaction['gas'] = 5000000
    transaction['gasPrice'] = w3.eth.gasPrice

    signed = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('Factory Contract Address:', tx_receipt.contractAddress)

    factory = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=compiled_contract['abi']
    )
    print('Manager:', factory.functions.manager().call())

    return tx_receipt.contractAddress


def wallet_contract(compiled_contract, address, user):
    factory = w3.eth.contract(
        address=address,
        abi=compiled_contract['abi']
    )

    value = Web3.toWei(.3, 'ether')
    transaction = factory.functions.createWallet(
        name="John Test",
        home="1 Main St., San Francisco, CA",
        tin="111-22-9999",
        phone="601-555-0055"
    ).buildTransaction({
        'from': user.account_address,
        'value': value,
        'nonce': w3.eth.getTransactionCount(user.account_address)
    })

    account = get_account()
    signed = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    print("Deployed Wallet: ", factory.functions.getDeployedWallets().call()[0])

def get_deployedWallets(compiled_contract):
    factory = w3.eth.contract(
        address='0x78f0c8357503352B96Af97f6D25439BA1d80a3B7',
        abi=compiled_contract['abi']
    )

    wallets = factory.functions.getDeployedWallets().call()
    return wallets[0]


w3.middleware_onion.inject(geth_poa_middleware, layer=0)

factory = compiled_factory()
wallet = compiled_wallet()
user = get_user()

factory_address = factory_contract(factory, user)
wallet_contract(factory, factory_address, user)
# print(get_deployedWallets(factory))



