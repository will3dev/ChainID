import re
import datetime
from KYC_WalletApp.models.models import User, Activity
from KYC_WalletApp.users.utils_dataVisualization import day_range


# check to see if password is valid format
# requirements:
# 8 characters, 1 upper, 1 lower, 1 number
def validate_password(password):
    u = re.search(r"[A-Z]", password)
    l = re.search(r"[a-z]", password)
    n = re.search(r"[0-9]", password)

    if len(password) >= 8 and u and l and n:
        return True
    else:
        return False

# ensure email is validate format
def validate_emailTool(email):
    a = re.search(r"\w+@\w+\.[a-zA-Z0-9]{2,3}", email)

    if a:
        return True
    else:
        return False

# ensure pw and confirm_pw match
def is_pwMatch(pw, confirm_pw):
    if pw == confirm_pw:
        return True
    else:
        return False


def get_userActivityLog():
    dates = list()
    today = datetime.datetime.utcnow()
    for x in range(day_range, 0, -1):
        date = today - datetime.timedelta(days=x)
        dates.append(date.date())

    activities = Activity.query.all()
    activity_log = [
        a for a in activities
        if a.create_datetime.date() in dates
    ]

    return activity_log


