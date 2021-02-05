import json, time
from web3 import exceptions
from KYC_WalletApp.w3.rinkey_connection import Connection
from KYC_WalletApp.w3.Wallet_Contract import Wallet_Contract as wc
from KYC_WalletApp.w3.Wallet_Factory import factory
from KYC_WalletApp.wallets.forms import ApproveWalletForm, GetWalletDataForm
from eth_account import Account

w3 = Connection.CONNECTION
wc = wc()


def getAccount(user, password):
    ks = json.loads(user.keystore)
    pk = w3.eth.account.decrypt(ks, password).hex()
    return Account.from_key(pk)


def createKYCWallet(account, name, home, tin, phone):
    fee = factory.functions.createWalletFee().call()
    transaction = factory.functions.createWallet(
        name=name,
        home=home,
        tin=tin,
        phone=phone
    ).buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'value': fee
    })
    try:
        signed = account.sign_transaction(transaction)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash)

        return 1

    except exceptions.SolidityError as err:
        return str(err)


def requestData(account, wallet, requester_name, request_desc):

    transaction = wallet.functions.makeRequest(
        name=requester_name,
        description=request_desc
    ).buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'value': w3.toWei(.25, 'ether')
    })

    try:
        signed = account.sign_transaction(transaction)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash)

        return 1

    except exceptions.SolidityError as error:
        return str(error)

def getRequests(address):
    wallet = wc.Wallet(address)
    requests = wallet.functions.getRequests().call()

    request_data = list()

    for request in requests:
        r = wallet.functions.requests(request).call()

        data = dict()
        data['requester'] = r[0]
        data['name'] = r[1]
        data['description'] = r[2]
        data['approved'] = r[3]
        #data['active'] = r[4]
        data['wallet'] = address
        data['pos'] = len(request_data)-1

        sub_form = ApproveWalletForm(
            requester=data['requester']
            # request_id = data['id']
        )
        data['form'] = sub_form
        request_data.append(data)

    return request_data


def getRequests_WalletData(wallet_address, user_accountAddress):
    wallet = wc.Wallet(wallet_address)
    requests = wallet.functions.getApprovedRequests().call() # get active requests
    active_requests = wallet.functions.getRequests().call()

    if (user_accountAddress in requests) or (user_accountAddress in active_requests):
        r = wallet.functions.requests(user_accountAddress).call()
        data = dict()
        data['requester'] = r[0]
        data['description'] = r[2]
        data['approved'] = r[3]
        data['active'] = r[4]
        data['wallet'] = wallet_address

        form = GetWalletDataForm(
            wallet=wallet_address,
            requester=data['requester']
        )

        data['form'] = form

        return data

def getRequestsMade_Active(wallet_address, user_accountAddress):
    wallet = wc.Wallet(wallet_address)
    requests = wallet.functions.getApprovedRequests().call()  # get active requests
    active_requests = wallet.functions.getRequests().call()

    if (user_accountAddress in requests) or (user_accountAddress in active_requests):
        r = wallet.functions.requests(user_accountAddress).call()
        if r[4]: # check to see if the request is active

            data = dict()
            data['wallet'] = wallet_address
            data['requester'] = r[0]
            data['description'] = r[2]
            data['approved'] = r[3]
            data['active'] = r[4]

            return data





def approveRequest(account, requester, address):
    walletContract = wc.Wallet(address)
    transaction = walletContract.functions.approveRequest(requester).buildTransaction({
        'nonce': w3.eth.getTransactionCount(account.address),
        'from': account.address
    })

    try:
        signed = account.sign_transaction(transaction)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash)

        return 1

    except exceptions.SolidityError as error:
        return str(error)

def getData_request(account, address):
    walletContract = wc.Wallet(address)

    eventFilter = walletContract.events.WalletData.createFilter(fromBlock="latest")

    try:
        transaction = walletContract.functions.getKYCData().buildTransaction({
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address)
        })
        signed = account.sign_transaction(transaction)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash)

    except exceptions.SolidityError as error:
        return str(error)



    while True:
        try:
            event = eventFilter.get_new_entries()[-1]
            data = event.args
            break
        except:
            pass

    return data

def getWalletEventData(address, tx_hash):
    walletContract = wc.Wallet(address)
    eventFilter = walletContract.events.WalletData.createFilter(fromBlock="latest")
    event = eventFilter.get_new_entries()
    return event

    #if event.transactionHash == tx_hash:
     #   return event.args
    #else:
     #   return 0


def getRequestDetails(user_accountAddress):
    # get a list of all deployed wallets
    deployedWallets = factory.functions.getDeployedWallets().call()

    # iterate over list of wallets and
    # check to see if user has any active requests
    allRequests = list()
    for wallet in deployedWallets:
        request_details = getRequests_WalletData(wallet, user_accountAddress)
        if request_details:
            allRequests.append(request_details)

    return allRequests

def getRequestsCounts(user_accountAddress):
    data = {
        "approved": 0,
        "pending": 0,
        "expense": 0,
    }

    deployedWallets = factory.functions.getDeployedWallets().call()
    for wallet_address in deployedWallets:
        wallet = wc.Wallet(wallet_address)
        approved_requests_count = wallet.functions.getApprovedRequests().call().count(user_accountAddress)
        pending_requests_count = wallet.functions.getRequests().call().count(user_accountAddress)

        expense = (
            w3.fromWei(wallet.functions.serviceCost().call(), 'ether')
                       ) * (approved_requests_count + pending_requests_count)

        data["approved"] += approved_requests_count
        data["pending"] += pending_requests_count
        data["expense"] += expense

    return data

def createWalletDict(manager, owner, serviceCost, request_ids, approved_requests):
    fee = w3.fromWei(serviceCost, 'ether')
    earnings = (fee/4) * approved_requests
    return {
        "manager": manager,
        "owner": owner,
        "service_cost": fee,
        "active_requests_count": request_ids,
        "approved_requests_count": approved_requests,
        "earnings": earnings
    }

def getMyWalletData(user_accountAddress):
    wallet_address = factory.functions.walletOwners(user_accountAddress).call()

    wallet = wc.Wallet(wallet_address)
    details = wallet.functions.getWalletDetails().call()
    return createWalletDict(*details)


def updateRequestFee(account, ether_value):
    amount = w3.toWei(ether_value, 'ether')


    try:
        transaction = factory.functions.updateRequestFee(amount).buildTransaction({
            'nonce': w3.eth.getTransactionCount(account.address),
            'from': account.address
        })
        signed = account.sign_transaction(transaction)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash)

        return 1
    except exceptions.SolidityError as error:
        return str(error)








