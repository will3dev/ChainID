from flask import (render_template, Blueprint)
from flask_login import login_required
from KYC_WalletApp.w3.Wallet_Factory import factory
from KYC_WalletApp.w3.Wallet_Contract import Wallet_Contract
from KYC_WalletApp.main.forms import WalletSearchForm
from KYC_WalletApp.w3.rinkey_connection import w3

main = Blueprint('main', __name__)

@main.route('/', methods=["GET", "POST"])
@main.route('/home', methods=["GET", "POST"])
@login_required
def home():
    wallets = factory.functions.getDeployedWallets().call()
    form = WalletSearchForm()

    data = {"process_requests": 0, "pending_requests": 0}

    for wallet in wallets:
        walletContract = Wallet_Contract().Wallet(wallet)
        walletData = walletContract.functions.getWalletDetails().call()
        data["process_requests"] += walletData[4]
        data["pending_requests"] += walletData[3]

    factoryData = factory.functions.getFactoryData().call()
    data["createFee"] = w3.fromWei(factoryData[0], 'ether')
    data["requestFee"] = w3.fromWei(factoryData[1], 'ether')
    data["wallets"] = len(wallets)

    return render_template("home.html", wallets=wallets, form=form, data=data)