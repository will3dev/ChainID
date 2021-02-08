from flask import (flash, request, redirect, url_for,
                   render_template, Blueprint)
from flask_login import login_required, current_user
from KYC_WalletApp import flask_bcrypt
from KYC_WalletApp.mail_utilities.utils import *
from KYC_WalletApp.models.utils import *
from KYC_WalletApp.wallets.forms import RequestDataForm, CreateWalletForm
from KYC_WalletApp.wallets.utils import *


wallets = Blueprint('wallets', __name__)
w3 = Connection.CONNECTION

@wallets.route("/requests_manager/<string:address>", methods=["GET", "POST"])
@login_required
def requests_manager(address):
    # get request details from all the wallets on the address
    all_requests = getRequestDetails(current_user.account_address)
    request_activity = getRequestsCounts(current_user.account_address)

    log_activity_successWeb(user=current_user, request_name="manage_requests")

    if request.form:
        if "requester" in request.form:

            form = all_requests[0]['form']
            if form.validate_on_submit():
                if form.validate_on_submit():
                    account = getAccount(current_user, form.password.data)
                    data = getData_request(
                        account=account,
                        address=form.wallet.data,
                    )

                    # check to see if error message was returned
                    if type(data) != str:
                        wallet_data = {
                            'wallet': form.wallet.data,
                            'requester': form.requester.data
                        }

                        all_requests = getRequestDetails(current_user.account_address)

                        log_activity_successWeb(user=current_user, request_name="get_wallet_data")

                        flash("Data successfully retrieved.", "success")
                        return render_template("requests_manager.html", requests=all_requests,
                                               wallet_data=wallet_data, request_activity=request_activity, user_data=data)

                    else:
                        log_activity_failureWeb(user=current_user, request_name="get_wallet_data")
                        flash(f"ERROR: {data}", "danger")

    return render_template("requests_manager.html", requests=all_requests, request_activity=request_activity)


@wallets.route("/manage_wallet", methods=["GET", "POST"])
@login_required
def manage_wallet():
    address = factory.functions.walletOwners(current_user.account_address).call()
    # if wallet address does not exist
    # contract returns "0x0000000000000000000000000000000000000000"
    # redirect to have user create a wallet
    if address == "0x0000000000000000000000000000000000000000":
        return redirect(url_for("wallets.create_wallet"))

    requests = getRequests(address)
    wallet_data = getMyWalletData(current_user.account_address)

    log_activity_successWeb(user=current_user, request_name="manage_wallet_requests")

    if request.form:
        if "requester" in request.form:

            # get POST request objects
            form = requests[0]['form']
            if form.validate_on_submit():
                if form.validate_on_submit():
                    account = getAccount(current_user, form.password.data)

                    approval = approveRequest(account=account, requester=form.requester.data, address=address)
                    # check to see if teh approval was successful
                    if approval == 1:
                        log_activity_successWeb(user=current_user, request_name="manage_wallet_approve")

                        # alert the requester that the request has been approved
                        requestApprovedAlert(recipient_account=form.requester.data, wallet_address=address)
                        flash(f"Request from {form.requester.data} approved.", "success")
                        return redirect(url_for("wallets.manage_wallet"))

                    # on failure flash solidity error message
                    else:
                        log_activity_failureWeb(user=current_user, request_name="manage_wallet_approve")
                        flash(f"Request from {form.requester.data} approval failure.\n{approval}", "danger")

    return render_template("manage_wallet.html", requests=requests, address=address, wallet_data=wallet_data)


@wallets.route("/create_wallet", methods=["GET", "POST"])
@login_required
def create_wallet():

    form = CreateWalletForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()

        if flask_bcrypt.check_password_hash(user.password, form.password.data):
            account = getAccount(user, form.password.data)
            # compound the address to one line
            address = form.street.data + ', ' + form.city.data + ', ' + form.state.data

            wallet_create = createKYCWallet(
                account=account,
                factory=factory,
                name=form.name.data,
                home=address,
                tin=form.tin.data,
                phone=form.phone.data
            )
            # if create wallet was a success
            if wallet_create == 1:
                wallet_address = factory.functions.walletOwners(user.account_address).call()
                log_activity_successWeb(user=current_user, request_name="create_wallet")
                walletCreatedAlert(recipient=current_user, wallet_address=wallet_address)
                flash(f"New wallet created at {wallet_address}.", "success")
                return redirect(url_for("wallets.manage_wallet"))

            # wallet create fails flash the solidity error message
            else:
                log_activity_failureWeb(user=current_user, request_name="create_wallet")
                flash(f"Creation of wallet failed. {wallet_create}", "danger")

        else:
            log_activity_failureWeb(user=current_user, request_name="create_wallet")
            flash("Password incorrect.", "danger")

    return render_template("create_wallet.html", form=form)

@wallets.route("/request_data/<address>", methods=["GET", "POST"])
@login_required
def request_data(address):
    form = RequestDataForm()
    wallet = wc.Wallet(address)
    # unpack the required values for the route
    manager, owner, fee, *_discard = wallet.functions.getWalletDetails().call()
    fee = w3.fromWei(fee, 'ether')

    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()

        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            account = getAccount(user, form.password.data)

            # check to see if there is already a request made by this account
            if user.account_address in wallet.functions.getRequests().call():
                log_activity_successWeb(user=current_user, request_name="request_wallet_data")

                flash(f"You have already made a pending request to {address}.", "warning")
                return redirect(url_for("main.home"))

            # otherwise make a new request
            else:
                wallet_data_request = requestData(
                    account=account,
                    wallet=wc.Wallet(address),
                    requester_name=form.requester.data,
                    request_desc=form.request_reason.data
                )
                # if the request is a success
                if wallet_data_request == 1:
                    log_activity_successWeb(user=current_user, request_name="request_wallet_data")
                    # send email notifying owner of request
                    newRequestAlert(recipient_account=owner)
                    flash(f"Request for data sent to {address}.", "success")
                    return redirect(url_for("main.home"))

                # if the data request fails redirect and flash the Solidity error message
                else:
                    log_activity_failureWeb(user=current_user, request_name="request_wallet_data")
                    flash(f"{wallet_data_request}", "danger")
        else:
            log_activity_failureWeb(user=current_user, request_name="request_wallet_data")
            flash("Password incorrect", "danger")
    return render_template("request_data.html", address=address, fee=fee, manager=manager, owner=owner, form=form)