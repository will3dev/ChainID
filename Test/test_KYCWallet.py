import os
import pytest
from solcx import compile_source
from web3 import Web3
from eth_account import Account

ganache_url = 'HTTP://127.0.0.1:7545'

accounts = [
    '0x045d149369D7128aEa243e27A3711ad915f72D9D',
    '0x989E53e912820c86F51f6F1D9FE3BD092B45760E',
    '0x316e4e4D8391730ACB7f1c6533c1780208A168Ed',
    '0x3Df18D93A21C04f158F10d07d1356f60489d0827'
]

keys = [
    '9b100a6b7f35edc447a7d741504d34c1f6ab6e5b7ff52114ec89d34cfa8fc0ca',
    '6be8dc2b52f57ebabe0914943456a71d2572371cdb11eb3b2787b076649e2e6c',
    '36e95d6450266454f891524169ce5bbdca693e78db23790c1aa38264c4c7cb81',
    '915f95b9a2729ee329de8af7ac4864696f31dfb442c8649a624ae31581b9d760',
]

FEES = Web3.toWei(.5, 'ether')

@pytest.fixture
def tester_provider():
    return Web3.HTTPProvider(ganache_url)

@pytest.fixture
def w3(tester_provider):
    return Web3(tester_provider)

@pytest.fixture
def compiled_contract():
    contract_path = os.path.join(os.getcwd(), '..', 'Contract', 'KYCWallet_Contract_UPDATED.sol')

    with open(contract_path, 'r') as f:
        source = f.read()

    return compile_source(source)

@pytest.fixture
def factory_contract(w3, compiled_contract):
    factory = compiled_contract['<stdin>:WalletFactory']

    deploy_address = accounts[0]

    WalletFactoryContract = w3.eth.contract(
        abi=factory['abi'],
        bytecode=factory['bin']
    )

    tx_hash = WalletFactoryContract.constructor(
        FEES,
        FEES).transact({
        'from': deploy_address,
    })

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    return WalletFactoryContract(tx_receipt.contractAddress)

@pytest.fixture
def wallet_contract(factory_contract, w3, compiled_contract):
    value = w3.toWei(.6, 'ether')
    transaction = factory_contract.functions.createWallet(
        name="John Test",
        home="1 Main St, San Francisco, CA",
        tin="000-99-8888",
        phone="732-555-0055"
    ).buildTransaction({
        'from': accounts[1],
        'value': value,
        'nonce': w3.eth.getTransactionCount(accounts[1])
    })

    acct = Account.from_key(keys[1])
    signed = acct.sign_transaction(transaction)
    w3.eth.sendRawTransaction(signed.rawTransaction)
    #w3.eth.waitForTransactionReceipt(tx_hash)

    walletContract = compiled_contract['<stdin>:KYC_Wallet']

    address = factory_contract.functions.getDeployedWallets().call()[0]
    Contract = w3.eth.contract(abi=walletContract['abi'], address=address)

    return Contract


@pytest.fixture
def WalletData_filter(wallet_contract):
    return wallet_contract.events.WalletData.createFilter(fromBlock="latest")


def test_deploys_contractFactory(factory_contract):
    manager = factory_contract.functions.manager().call()
    create_fee = factory_contract.functions.createWalletFee().call()
    request_fee = factory_contract.functions.dataRequestFee().call()

    assert manager == accounts[0]
    assert create_fee == FEES
    assert request_fee == FEES

def test_walletOwner_deployWallet(factory_contract, wallet_contract):
    walletOwner = factory_contract.functions.walletOwners(accounts[1]).call()
    wallet = factory_contract.functions.getDeployedWallets().call()
    assert walletOwner == wallet[0]

def test_deploys_Wallet(wallet_contract):
    manager = wallet_contract.functions.manager().call()
    owner = wallet_contract.functions.owner().call()
    assert manager == accounts[0]
    assert owner == accounts[1]

def test_walletData(wallet_contract, w3):
    # test to make sure that admin and owner
    # can access wallet data
    data = ['John Test', '1 Main St, San Francisco, CA', '000-99-8888', '732-555-0055']
    transaction1 = wallet_contract.functions.getData().call({
        'from': accounts[0],
        'nonce': w3.eth.getTransactionCount(accounts[0])
    })
    transaction2 = wallet_contract.functions.getData().call({
        'from': accounts[1],
        'nonce': w3.eth.getTransactionCount(accounts[1])
    })

    assert transaction1 == data
    assert transaction2 == data

def test_walletData_failure(wallet_contract, w3):
    # test to make sure that wallet data
    # cannot be accessed by non-manager or non-owner
    try:
        transaction = wallet_contract.functions.getData().call({
            'from': accounts[2],
            'nonce': w3.eth.getTransactionCount(accounts[2])
        })

    except:
        transaction = None

    assert not transaction

def test_makeRequest(wallet_contract, w3):

    account = Account.from_key(keys[2])
    transaction = wallet_contract.functions.makeRequest(
        name="Test Business",
        description="To get some test data"
    ).buildTransaction({
        'from': accounts[2],
        'nonce': w3.eth.getTransactionCount(accounts[2]),
        'value': Web3.toWei(.5, 'ether')
    })

    signed = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    w3.eth.waitForTransactionReceipt(tx_hash)

    # getRequests returns active requests
    requestNum = wallet_contract.functions.getRequests().call()

    assert len(requestNum) == 1
    assert requestNum[0] == accounts[2]

def test_makeRequest_insufficientFee(wallet_contract, w3):
    try:
        account = Account.from_key(keys[3])
        transaction = wallet_contract.functions.makeRequest(
            name="Test Business",
            description="To get some test data"
        ).buildTransaction({
            'from': accounts[3],
            'nonce': w3.eth.getTransactionCount(accounts[3]),
            'value': Web3.toWei(.01, 'ether')
        })

        signed = account.sign_transaction(transaction)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash)
        assert False

    except:

        requestNum = wallet_contract.functions.getRequests().call()


    assert len(requestNum) == 0

def test_approveRequest_failure(wallet_contract, w3):
    account = Account.from_key(keys[2])
    transaction = wallet_contract.functions.makeRequest(
        name="Test Business",
        description="To get some test data"
    ).buildTransaction({
        'from': accounts[2],
        'nonce': w3.eth.getTransactionCount(accounts[2]),
        'value': Web3.toWei(.5, 'ether')
    })

    signed = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    w3.eth.waitForTransactionReceipt(tx_hash)

    try:
        # if this approve goes through it means this test failed
        wallet_contract.functions.approveRequest(1).call({
            'from': accounts[2],
            'nonce': w3.eth.getTransactionCount(accounts[2])
        })
        assert False

    except:
        assert True


def test_approveRequest(wallet_contract, w3, WalletData_filter):
    data = ['John Test', '1 Main St, San Francisco, CA', '000-99-8888', '732-555-0055']
    beforeBal_owner = w3.eth.getBalance(accounts[1])
    beforeBal_mngr = w3.eth.getBalance(accounts[0])

    # build the makeRequest transaction
    account = Account.from_key(keys[2])
    transaction = wallet_contract.functions.makeRequest(
        name="Test Business",
        description="To get some test data"
    ).buildTransaction({
        'from': accounts[2],
        'nonce': w3.eth.getTransactionCount(accounts[2]),
        'value': Web3.toWei(.6, 'ether')
    })

    # send the makeRequest transaction
    signed = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    w3.eth.waitForTransactionReceipt(tx_hash)

    # get the list of requests before
    # assert that there is only one item in the list
    requests_before = wallet_contract.functions.getRequests().call()
    r = requests_before[0] # get the address of the account that just made the request

    assert len(requests_before) == 1


    # create the approveRequest transaction
    approveTrans = wallet_contract.functions.approveRequest(r).buildTransaction({
        'from': accounts[1],
        'nonce': w3.eth.getTransactionCount(accounts[1])
    })
    approver = Account.from_key(keys[1])
    approveSigned = approver.sign_transaction(approveTrans)
    tx_hashApprove = w3.eth.sendRawTransaction(approveSigned.rawTransaction)
    w3.eth.waitForTransactionReceipt(tx_hashApprove)

    # get the list of the requests after being approved
    requests_after = wallet_contract.functions.getRequests().call()
    approved_requests_after = wallet_contract.functions.getApprovedRequests().call()
    assert len(requests_after) == 0
    assert len(approved_requests_after) == 1


    # now that the request has been approved, get the wallet data
    # build wallet data request
    walletDataTrans = wallet_contract.functions.getKYCData().buildTransaction({
        'from': accounts[2],
        'nonce': w3.eth.getTransactionCount(accounts[2])
    })
    walletDataSigned = account.sign_transaction(walletDataTrans)
    tx_hashWalletData = w3.eth.sendRawTransaction(walletDataSigned.rawTransaction)

    # check to see if new entries were added to event listener
    event = WalletData_filter.get_new_entries()[-1]
    if event.transactionHash == tx_hashWalletData:
        args = event.args
        wallet_data = [args[key] for key in list(args.keys())]

    assert wallet_data == data

    afterBal_owner = w3.eth.get_balance(accounts[1])
    afterBal_mngr = w3.eth.get_balance(accounts[0])

    assert beforeBal_mngr < afterBal_mngr
    assert beforeBal_owner < afterBal_owner




