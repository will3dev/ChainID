from flask import (flash, redirect, url_for,
                   render_template, Blueprint)
from flask_login import login_user, current_user, login_required, logout_user
from KYC_WalletApp import flask_bcrypt
from KYC_WalletApp.mail_utilities.utils import welcomeEmail
from KYC_WalletApp.users.forms import RegistrationForm, LoginForm, TransferForm
from KYC_WalletApp.models.utils import *
from KYC_WalletApp.wallets.utils import getAccount
from KYC_WalletApp.users.utils import *
from KYC_WalletApp.users.utils_dataVisualization import *
from KYC_WalletApp.w3.AccountTools import *


users = Blueprint('users', __name__)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        log_activity_successWeb(
            user=current_user,
            request_name="user_login"
        )
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            log_activity_successWeb(
                user=user,
                request_name="user_login"
            )

            login_user(user)

            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.home"))

        else:
            log_activity_failureWeb(
                user=user,
                request_name="user_login"
            )
            flash("Login unsuccessful. Please check log credentials.", "danger")
    return render_template("login.html", title="Login", form=form)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # create a keystore with the new users account
        account = create_account(form.password.data)
        # take the encrypted keystore and convert it
        # to be saved in the DB
        keystore = json.dumps(account.get("keystore"))
        # create the new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            account_address=account.get('address'),
            keystore=keystore
        )
        # send welcome email
        welcomeEmail(user)
        log_activity_successWeb(user=user, request_name="create_user")

        flash(f"Your account has been created!", "primary")
        return redirect(url_for('users.login'))
    return render_template("register.html", title="Register", form=form)


@users.route("/logout", methods=["GET"])
def logout():
    log_activity_successWeb(
        user=current_user,
        request_name="user_logout"
    )
    logout_user()
    return redirect(url_for('users.login'))


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    bal = get_account_balance(current_user.account_address)
    form = TransferForm()
    if form.validate_on_submit():
        if form.amount.data > bal:
            log_activity_failureWeb(
                user=current_user,
                request_name="transfer_ether",
            )
            flash("There are insufficient funds in the account.", "danger")
            return redirect(url_for('users.profile'))

        account = getAccount(current_user, form.password.data)
        transfer_ether(
            value=form.amount.data,
            to_account=form.to_address.data,
            from_account=account,
        )
        log_activity_successWeb(
            user=current_user,
            request_name="transfer_ether"
        )

        flash(f"{form.amount.data} ether successfully sent.", "success")
        return redirect(url_for('users.profile'))

    return render_template("profile.html", title="Profile", bal=bal, form=form)

@users.route("/admin_dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    log = get_userActivityLog()
    chart = generate_plt()



    return render_template("admin_dashboard.html", title="Dashboard", log=log, chart=chart)
