import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import mpld3
from KYC_WalletApp.models.models import Activity
from KYC_WalletApp import db

plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0

class ActivityDashboard:
    def __init__(self, day_range):
        self.df = pd.read_sql_query(Activity.query.statement, db.session.bind)
        self.day_range = day_range
        self.df_condensed = self.getDataActivityRange(self.df)

    def is_inRange(self, date, day_range):
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
    def getDataActivityRange(self, df):
        # sort the dataframe so it is descending
        sorted_df = df.sort_values(ascending=False, by=['id'])
        # iterate over all rows of dataframe
        valid_row = None
        for row in sorted_df.itertuples():
            # if the date is outside the range break
            created = row.create_datetime
            if not self.is_inRange(created, self.day_range):
                # return the first row found that is within range
                valid_row = row.Index + 1
                break
        # create new df that starts at the first valid row
        return df.iloc[valid_row:]

    def activity_by_hour(self):
        df = self.df_condensed

        # add in column showing the hour that activity occurred
        df['hour'] = df['create_datetime'].apply(lambda x: x.time().hour)
        hours_in_day = np.arange(0, 24)
        # group the activity together to get just the count by hours
        hours_activity = df.groupby('hour').count()['id'].to_dict()
        # make a list of the activity that can be used for y values
        # this will fill in any missing key values from the hours_in_day
        usage = list()
        for x in hours_in_day:
            usage.append(hours_activity.get(x, 0))

        usage = np.array(usage)
        return {'x': hours_in_day, 'y': usage}

    def activity_by_channel(self):
        df = self.df_condensed

        # set up dates object
        today = datetime.datetime.utcnow().date()
        dates = list()

        # append datetime objects to dates object
        # starting with date from 30 days ago through today
        for x in range(self.day_range - 1, -1 , -1):
            date = today - datetime.timedelta(days=x)
            dates.append(date)

        # create new column with just date objects instead of datetime objects
        df['date'] = df['create_datetime'].apply(lambda d: d.date())

        # create new column for the channel values converted to integers
        converter = {'api': 1, 'web': 0}
        df['channel_convert'] = df['channel'].apply(lambda c: converter[c])

        # separate out activity by channel
        api = df[df['channel_convert'] > 0]
        web = df[df['channel_convert'] < 1]

        # group the activity by date to get an activity count
        web_act = web.groupby('date').count()['request_name']
        api_act = api.groupby('date').count()['request_name']

        # join data together to one DF
        final_df = pd.DataFrame(index=sorted(dates)).join(web_act).join(api_act, rsuffix='_api', lsuffix='_web')
        final_df.fillna(value=0, inplace=True)

        return {'x': final_df.index, 'y_web': final_df['request_name_web'], 'y_api': final_df['request_name_api']}

    def activity_by_request_type(self):
        df = self.df_condensed

        # separate out the activity for api vs. web
        data_api = df[df['channel'] == 'api']
        data_web = df[df['channel'] == 'web']

        # group the data in both the dataframes by request name and get count
        api = data_api.groupby('request_name').count()['channel']
        web = data_web.groupby('request_name').count()['channel']

        # merge the two dataframes and fill in the NaN values
        channel_data = pd.merge(
            api, web,
            how='outer',
            on='request_name',
            suffixes=('_api', '_web')
        ).fillna(0)

        return channel_data

    def generate_plot(self):
        hours = self.activity_by_hour()
        channel = self.activity_by_channel()
        request = self.activity_by_request_type()

        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(9, 8))

        plt.tight_layout()

        ax[0].plot(channel['x'], channel['y_web'], label='Web', color='#0d6efd')
        ax[0].plot(channel['x'], channel['y_api'], label='API', color='#ffc107')
        ax[0].set_title('Channel Activity')
        ax[0].legend(loc=0)
        plt.setp(ax[0].xaxis.get_majorticklabels(), rotation=30)

        ax[1].plot(hours['x'], hours['y'], lw=3, color='#20c997')
        ax[1].set_xticks(hours['x'])
        ax[1].set_xticklabels(hours['x'])
        ax[1].set_title('Activity Volume by Hour')

        x = np.arange(len(request.index))  # get the xtick positions
        width = .35  # set the width of the bars

        ax[2].bar(
            x - width / 2,  # plot the x coordinates position left the amount of the width
            request['channel_api'],
            width,  # width of the bar
            label='API',
            color='#d63384'
        )

        ax[2].bar(
            x + width / 2,  # plot the x coordinates position right the amount of the width
            request['channel_web'],
            width,  # width of the bar
            label='Web',
            color='#6f42c1'
        )

        ax[2].set_title('Activity by Request Type')
        ax[2].set_xlabel('Request Type')
        ax[2].set_ylabel('Volume of Requests')
        ax[2].set_xticks(x)  # set where the x ticks will show up
        ax[2].set_xticklabels(list(request.index), rotation=45)  # set the labels for the xticks
        ax[2].legend()

        fig.tight_layout()

        return mpld3.fig_to_html(fig)









