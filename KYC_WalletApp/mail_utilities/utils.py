from flask_mail import Message
from KYC_WalletApp import mail
from KYC_WalletApp.models.models import User

def welcomeEmail(recipient):
    body = f"""
    Hello {recipient.username},\n
This is to alert you that you have successfully reigstered with ChainID. Your public account address is {recipient.account_address}.\n
To get started - check out the home page where you can see all active ID wallets. 
There you can click on the request button to request another user's data.\n
Want your own ID Wallet? Click on the navbar and click on manage wallet. 
If you are new to ChainID this is where you can create your own ID Wallet.\n
Feel free to reach out with any questions - general@will3dev.com.\n
    -ChainID Admin"""
    subject = "ID Wallet Created"
    sender = ('ChainID Admin', 'general@will3dev.com')
    recipients = [recipient.email]
    msg = Message(
        subject=subject,
        body=body,
        recipients=recipients,
        sender=sender
    )

    mail.send(msg)

def requestApprovedAlert(recipient_account, wallet_address):
    recipient = User.query.filter_by(account_address=recipient_account).first()
    body = f"""
Hello {recipient.username},\n
Your request to wallet {wallet_address} as been approved.\n
You can now go retrieve the wallet data.\n
-ChainID Admin"""
    subject = "Request Approved"
    sender = ('ChainID Admin', 'general@will3dev.com')
    recipients = [recipient.email]
    msg = Message(
        subject=subject,
        body=body,
        recipients=recipients,
        sender=sender
    )

    mail.send(msg)

def walletCreatedAlert(recipient, wallet_address):
    body = f"""
Hello {recipient.username},\n
This is to alert you that your ID Wallet has been created.\n
Wallet is located at {wallet_address}.\n
-ChainID Admin"""
    subject = "ID Wallet Created"
    sender = ('ChainID Admin', 'general@will3dev.com')
    recipients = [recipient.email]
    msg = Message(
        subject=subject,
        body=body,
        recipients=recipients,
        sender=sender
    )

    mail.send(msg)

def newRequestAlert(recipient_account):
    recipient = User.query.filter_by(account_address=recipient_account).first()
    body = f"Hello {recipient.username},\nThis is to alert you that a data request has been made to your ID Wallet.\n-ChainID Admin"
    subject = "Request Notification"
    sender = ('ChainID Admin', 'general@will3dev.com')
    recipients = [recipient.email]
    msg = Message(
        subject=subject,
        body=body,
        recipients=recipients,
        sender=sender
    )

    mail.send(msg)

