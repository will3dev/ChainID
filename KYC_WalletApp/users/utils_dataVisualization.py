import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import mpld3
from KYC_WalletApp.models.models import Activity
from KYC_WalletApp import db

day_range = 15

def is_inRange(date):
    # get the current date as utc datetime value
    now = datetime.datetime.utcnow()
    # get the delta
    delta = now - date
    # if the 'days' attribute is less than 30
    # return True else it is False
    if delta.days <= day_range:
        return True

    else:
        return False

# not very efficient
def getDataActivityRange(df):
    # sort the dataframe so it is descending
    sorted_df = df.sort_values(ascending=False, by=['id'])
    # iterate over all rows of dataframe
    valid_row = None
    for row in sorted_df.itertuples():
        # if the date is outside the range break
        created = row.create_datetime
        if not is_inRange(created):
            # return the first row found that is within range
            valid_row = row.Index + 1
            break
    # create new df that starts at the first valid row
    return df.iloc[valid_row:]


def generate_plt():
    df = pd.read_sql_query(Activity.query.statement, db.session.bind)
    prior30_df = getDataActivityRange(df)

    # take data and just return dates/get rid of time value
    prior30_df['create_datetime'] = prior30_df['create_datetime'].map(lambda x: x.date())

    # drop the id and user_id column
    prior30_df = prior30_df[['create_datetime', 'channel', 'request_name']]

    # get just the unique dates
    unique_dates_df = list(pd.unique(prior30_df['create_datetime']))
    # set up dates object
    today = datetime.datetime.utcnow().date()
    dates = [today]

    # append datetime objects to dates object
    # starting with date from 30 days ago through today
    for x in range(day_range, 1, -1):
        date = today - datetime.timedelta(days=x)
        dates.append(date)

    # get df of just api data
    df_api = prior30_df[df.channel == 'api']
    table_api = pd.pivot_table(
        df_api,
        values='request_name',
        columns='channel',
        index='create_datetime',
        aggfunc=pd.Series.count, # use this to count nonzero values in array
    )


    # get df of just web data
    df_web = prior30_df[df.channel == 'web']
    table_web = pd.pivot_table(
        df_web,
        values='request_name',
        columns='channel',
        index='create_datetime',
        aggfunc=pd.Series.count,
    )

    data = dict()
    for date in dates:
        data[str(date)] = {
            'api': 0,
            'web': 0
        }


    for row in table_web.itertuples():
        data[str(row.Index)]['web'] = row.web

    for row in table_api.itertuples():
        data[str(row.Index)]['api'] = row.api

    web_data = []
    api_data = []

    for date in data.keys():
        api_data.append(data[date]['api'])
        web_data.append(data[date]['web'])

    print(web_data)
    print(api_data)
    print(len(dates))


    y = max([max(web_data), max(api_data)])
    ymax = ((y // 5) + 1) * 5

    # x = [str(d) for d in dates]

    fig = plt.figure(figsize=(8, 6))
    plt.plot(dates, web_data, label="Web", color='#0d6efd')
    plt.plot(dates, api_data, label="API", color='#ffc107')
    plt.axis(ymax=ymax)


    plt.title('Wallet Activity')
    plt.ylabel('Activity Volume')
    plt.xlabel('Activity Dates')
    plt.xticks(rotation=45)
    plt.legend()

    return mpld3.fig_to_html(fig)


