from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt import JWT

from KYC_WalletApp.config import Config

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'warning'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='./templates',
        static_folder='./static'
    )
    app.config.from_object(Config)
    api = Api(app)

    db.init_app(app)
    flask_bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    from KYC_WalletApp.main.routes import main
    from KYC_WalletApp.users.routes import users
    from KYC_WalletApp.wallets.routes import wallets

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(wallets)

    from KYC_WalletAPI.resources.walletFactory import (DeployedWallets, WalletFactory,
                                                       WalletRequest, ManageWallet, ApproveRequest,
                                                       CreateNewWallet, ManageRequests, WalletData)

    api.add_resource(DeployedWallets, '/api/deployed_wallets')
    api.add_resource(WalletFactory, '/api/wallet_factory')
    api.add_resource(WalletRequest, '/api/wallet_request/<string:wallet_address>')
    api.add_resource(ManageWallet, '/api/manage_wallet/<string:wallet_address>')
    api.add_resource(ApproveRequest, '/api/approve_request/<string:wallet_address>')
    api.add_resource(CreateNewWallet, '/api/wallet_factory/create_wallet')
    api.add_resource(ManageRequests, '/api/requests_made_activity')
    api.add_resource(WalletData, '/api/retrieve_wallet_data/<string:wallet_address>')

    return app
