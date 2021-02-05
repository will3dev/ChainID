from KYC_WalletApp import db
from KYC_WalletApp.models.models import Activity

def log_activity(user, request_name, status, channel):
    activity = Activity(
        request_name=request_name,
        status=status,
        channel=channel
    )

    try:
        user.activity_log.append(activity)
        db.session.add(user)
        db.session.commit()

        return 1
    except:
        return 0


def log_activity_successWeb(user, request_name):
    activity = Activity(
        request_name=request_name,
        status="success",
        channel="web"
    )

    try:
        user.activity_log.append(activity)
        db.session.add(user)
        db.session.commit()

        return 1
    except:
        return 0


def log_activity_failureWeb(user, request_name):
    activity = Activity(
        request_name=request_name,
        status="failure",
        channel="web"
    )

    try:
        user.activity_log.append(activity)
        db.session.add(user)
        db.session.commit()

        return 1
    except:
        return 0


def log_activity_successAPI(user, request_name):
    activity = Activity(
        request_name=request_name,
        status="success",
        channel="api"
    )

    try:
        user.activity_log.append(activity)
        db.session.add(user)
        db.session.commit()

        return 1
    except:
        return 0


def log_activity_failureAPI(user, request_name):
    activity = Activity(
        request_name=request_name,
        status="failure",
        channel="api"
    )

    try:
        user.activity_log.append(activity)
        db.session.add(user)
        db.session.commit()

        return 1
    except:
        return 0