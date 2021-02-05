
from flask_restful import Resource, reqparse
from KYC_WalletApp.w3.Wallet_Contract import Wallet_Contract
from KYC_WalletApp.w3.rinkey_connection import w3
from KYC_WalletApp.models.models import User
from KYC_WalletApp.models.utils import *
from KYC_WalletApp.wallets.utils import *


class DeployedWallets(Resource):
    def get(self):
        wallets = factory.functions.getDeployedWallets().call()
        return {"deployed_wallets": wallets}


class WalletFactory(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        #location='form',
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        #location='form',
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('amount',
                        type=float,
                        #location='form',
                        required=True,
                        help="Must provide amount in Ether"
                        )

    def get(self):
        data = factory.functions.getFactoryData().call()

        return {
            "manager": data[2],
            "create_wallet_fee": str(w3.fromWei(data[0], 'ether')) + ' ether',
            "data_request_fee": str(w3.fromWei(data[1], 'ether')) + ' ether'
        }

    def put(self):
        data = WalletFactory.parser.parse_args()

        user = User.query.filter_by(username=data["username"]).first()
        account = getAccount(user, data["password"])



        feeUpdate = updateRequestFee(account, data["amount"])
        if feeUpdate == 1:
            log_activity_successAPI(user=user, request_name="update_request_fee")
            return {"data_request_fee": (
                        str(w3.fromWei(factory.functions.dataRequestFee().call(), 'ether')) + ' ether'
            )}

        else:
            log_activity_failureAPI(user=user, request_name="update_request_fee")
            return {"message": feeUpdate}

class CreateNewWallet(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('owner_name',
                        type=str,
                        required=True,
                        help="Must provide name"
                        )
    parser.add_argument('street',
                        type=str,
                        required=True,
                        help="Must provide street address"
                        )
    parser.add_argument('city',
                        type=str,
                        required=True,
                        help="Must provide name"
                        )
    parser.add_argument('state_ZIP',
                        type=str,
                        required=True,
                        help="Must provide name"
                        )
    parser.add_argument('tax_id',
                        type=str,
                        required=True,
                        help="Must provide name"
                        )
    parser.add_argument('phone_number',
                        type=str,
                        required=True,
                        help="Must provide name"
                        )

    def post(self):
        data = CreateNewWallet.parser.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        account = getAccount(user, data["password"])

        if factory.functions.walletOwners(user.account_address).call() != "0x0000000000000000000000000000000000000000":
            return {"message": "This user already has an existing wallet. Limit is one."}

        address = (
            data["street"] + ', ' +
            data["city"] + ', ' +
            data["state_ZIP"]
        )

        wallet = createKYCWallet(
            account=account,
            name=data["owner_name"],
            home=address,
            tin=data["tax_id"],
            phone=data["phone_number"]
        )

        if wallet == 1:
            log_activity_successAPI(user=user, request_name="create_wallet")

            wallet_address = factory.functions.walletOwners(user.account_address).call()
            return {"wallet_address": wallet_address}

        else:
            log_activity_failureAPI(user=user, request_name="create_wallet")
            return {"message": wallet}







class WalletRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('requesterName',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('requestDescription',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )


    def get(self, wallet_address):
        if wallet_address not in factory.functions.getDeployedWallets().call():
            return {"message": "Wallet '{}' is not in the list of deployed wallets".format(wallet_address)}, 400

        wallet = Wallet_Contract().Wallet(wallet_address)
        (manager, owner, data_request_fee,
         pending_requests, approved_requests) = wallet.functions.getWalletDetails().call()

        return {
            "walletAddress": wallet_address,
            "manager": manager,
            "owner": owner,
            "data_request_feee": str(w3.fromWei(data_request_fee, 'ether')) + ' ether',
            "pending_request_count": pending_requests,
            "approved_request_count": approved_requests,
        }, 200

    def post(self, wallet_address):

        data = WalletRequest.parser.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        account = getAccount(user, data["password"])

        if wallet_address not in factory.functions.getDeployedWallets().call():
            log_activity_failureAPI(user=user, request_name="request_wallet_data")
            return {"message": "Wallet '{}' is not in the list of deployed wallets".format(wallet_address)}, 400

        wallet = Wallet_Contract().Wallet(wallet_address)

        request = requestData(
                    account=account,
                    wallet=wallet,
                    requester_name=data["requesterName"],
                    request_desc=data["requestDescription"]
                )
        if request == 1:

            log_activity_successAPI(user=user, request_name="request_wallet_data")

            (requester, company_name, request_description,
             is_approved, is_active) = wallet.functions.requests(account.address).call()
            return {"walletAddress": wallet_address,
                    "requester_address": requester,
                    "company_name": company_name,
                    "request_description": request_description,
                    "is_approved": is_approved,
                    "is_active": is_active}, 201

        else:
            log_activity_failureAPI(user=user, request_name="request_wallet_data")
            return {"message": request}



class ManageWallet(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )

    def get(self, wallet_address):
        data = ManageWallet.parser.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        wallet = Wallet_Contract().Wallet(wallet_address)

        if wallet.functions.owner().call() != user.account_address:
            log_activity_successAPI(user=user, request_name="manage_wallet_requests")
            return {"message": "This is only available for the owner of the wallet."}

        # get list of active requests
        request_list = [
            wallet.functions.requests(i).call()
            for i in wallet.functions.getRequests().call()
        ]

        requests = [
            {
                "requester_address": r[0],
                "company_name": r[1],
                "request_description": r[2],
                "is_approved": r[3],
                "is_active": r[4]
            }
            for r in request_list
        ]

        log_activity_successAPI(user=user, request_name="manage_wallet_requests")

        return {"wallet_address": wallet_address,
                "requests": requests}



class ApproveRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('requester_address',
                        type=str,
                        required=True,
                        help="This field is needed to approve a request"
                        )

    def put(self, wallet_address):
        data = ApproveRequest.parser.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        account = getAccount(user, data["password"])

        # approve the request provided in the call body
        approval = approveRequest(account=account, requester=data["requester_address"], address=wallet_address)
        if approval == 1:

            # now that request is approved, get the request detail
            wallet = Wallet_Contract().Wallet(wallet_address)
            request = wallet.functions.requests(data["requester_address"]).call()

            log_activity_successAPI(user=user, request_name="manage_wallet_approve")

            return {
                "wallet_address": wallet_address,
                "request": {
                    "requester_address": request[0],
                    "company_name": request[1],
                    "request_description": request[2],
                    "is_approved": request[3],
                    "is_active": request[4]
                }
            }, 202

        else:
            log_activity_failureAPI(user=user, request_name="manage_wallet_approve")

            # if there is an error return the Solidity error message
            return {"message": approval}, 400

class WalletData(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )

    def get(self, wallet_address):
        data = WalletData.parser.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        account = getAccount(user, data["password"])

        wallet_data = getData_request(account=account, address=wallet_address)

        # if return value is string, it means there was an error
        if type(wallet_data) is str:
            log_activity_failureAPI(user=user, request_name="get_wallet_data")

            # return the error message
            return {"message": wallet_data}

        else:
            log_activity_successAPI(user=user, request_name="get_wallet_data")

            return {
                "name": wallet_data.get("name"),
                "phone": wallet_data.get("phone"),
                "tax_id": wallet_data.get("tin"),
                "home": wallet_data.get("home")
            }

class ManageRequests(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank"
                        )

    def get(self):
        data = ManageRequests.parser.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        account = getAccount(user, data["password"])

        # get a list of all deployed wallets
        wallets = factory.functions.getDeployedWallets().call()

        # iterate over wallets and check to see if request was made by user
        active_requests = list()
        for wallet in wallets:
            # only gets active requests
            request_data = getRequestsMade_Active(wallet, account.address)
            if request_data:
                active_requests.append(request_data)

        log_activity_successWeb(user=user, request_name="manage_requests")

        return {"requests": active_requests}







