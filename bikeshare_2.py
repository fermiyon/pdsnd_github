import time
import pandas as pd
import numpy as np 
from dataclasses import dataclass
import json
import math
from colorama import Fore, Style

@dataclass
class Filters:
    """
    A Filters class to manage filter states based on string inputs.
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    city: str = ''
    month: str = ''
    day: str = ''

    @property
    def city_filter(self):
        """True if city filter is applied"""
        return self.city != ''

    @property
    def month_filter(self):
        """True if month filter is applied"""
        return self.month != ''

    @property
    def day_filter(self):
        """True if day filter is applied"""
        return self.day != ''


filters = Filters()

CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        Filter class that includes:
            (str) city - name of the city to analyze
            (str) month - name of the month to filter by, or "all" to apply no month filter
            (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    print('\nHello! Let\'s explore some US bikeshare data!')
    # get user input for city (chicago, new york city, washington). HINT: Use a while loop to handle invalid inputs
    while True:
        city = input(f'\n{Fore.GREEN}Would you like to see data for Chicago, New York, Washington or for all?{Style.RESET_ALL}\n').strip().lower()
        cities = list(CITY_DATA.keys()) + ['all']
        if city in cities:
            print(f'\nLooks like you want to hear about {city.capitalize()}! If this is not true, restart the program now!')
            if city != 'all':
                filters.city = city
            break
        else:
            print(f'\nInvalid input "{city}"! Please enter either {', '.join([x.capitalize() for x in cities])} as a city name.\n')

    # get user input for month (all, january, february, ... , june)
    time_filter_inputs = ['month','day','both','none']
    while True:
        time_filter = input(f"\n{Fore.GREEN}Would you like to filter the data by month, day, both or not at all?: Type 'none' for no time filter.{Style.RESET_ALL}\n").strip().lower()
        if time_filter in time_filter_inputs:
            break
        else:
            print(f"\nInvalid input!({time_filter}) Please enter either: {', '.join([x.capitalize() for x in time_filter_inputs])}")
    
    # no time filtering by default

    if time_filter != 'none':
        # get user input for month (all, january, february, ... , june)
        if time_filter in ('both','month'):
            month_inputs = ['all','january', 'february', 'march', 'april', 'may', 'june']
            months = ['january', 'february', 'march', 'april', 'may', 'june']
            while True:
                month = input(f'{Fore.GREEN}\nWhich month? {', '.join([x.capitalize() for x in months])}?{Style.RESET_ALL}\n').strip().lower()
                if month in month_inputs:
                    if month != 'all':
                        filters.month = month
                    break
                else:
                    print(f"\nInvalid input!({month}) Please enter either: {', '.join([x.capitalize() for x in month_inputs])}")

        if time_filter in ('both','day'):
            # get user input for day of week (all, monday, tuesday, ... sunday)
            while True:
                day = input(f'{Fore.GREEN}\nWhich day? Please type your response as a string. (e.g. Monday, Tuesday)):{Style.RESET_ALL}\n').strip().lower()
                day_inputs = ['all','monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                if day in day_inputs:
                    if day != 'all':
                        filters.day = day
                    break
                else:
                    print(f"\nInvalid input!({day}) Please enter either: {', '.join(day_inputs)}")
    

    print('-'*40)
    return filters


def load_data(filters:Filters):
    """
    Loads data for the specified city and filters by month and day if applicable.
    """
    # load data file into a dataframe
    try:
        if filters.city_filter:
            city_csv = f'{CITY_DATA[filters.city]}'
            df = pd.read_csv(city_csv)
            if 'Unnamed: 0' in df.columns:
                df.drop(['Unnamed: 0'], inplace=True, axis = 1)
        else:
            city_csv_list = list(CITY_DATA.values())
            df_list = []
            for city_csv in city_csv_list:
                df_ = pd.read_csv(city_csv)
                df_['state'] = city_csv.split()[0]
                df_list.append(df_)
            df = pd.concat(df_list)
            if 'Unnamed: 0' in df.columns:
                df.drop(['Unnamed: 0'], inplace=True, axis = 1)

    except:
        print('File Not Found!')
    else:
        # convert the Start Time column to datetime
        df['Start Time'] = pd.to_datetime(df['Start Time'])

        # extract month and day of week from Start Time to create new columns

        df['month'] = df['Start Time'].dt.month
        df['day_of_week'] = df['Start Time'].dt.day_name()
        df['start_hour'] = df['Start Time'].dt.hour


        # filter by month if applicable
        if filters.month_filter:
            # use the index of the months list to get the corresponding int
            months = ['january', 'february', 'march', 'april', 'may', 'june']
            try:
                month = months.index(filters.month.strip().lower())
            except:
                print("Please enter a month")
        
            # filter by month to create the new dataframe
            df = df[df['month'] == month + 1]

        # filter by day of week if applicable
        if filters.day_filter:
            # filter by day of week to create the new dataframe
            try:
                df = df[df['day_of_week'] == filters.day.capitalize()]
            except:
                print('Please enter a day name')
    
    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    # display the most common month
    # if there are both month and day filters do not show that
    if not (filters.month_filter & filters.day_filter):
        popular_month = df['month'].mode()[0]
        popular_month_count = df[df['month'] == popular_month].shape[0]
        print(f'Most popular month: {popular_month}, Count:{popular_month_count}')

        # display the most common day of week
        popular_day = df['day_of_week'].mode()[0]
        popular_day_count = df[df['day_of_week'] == popular_day].shape[0]
        print(f'Most popular day: {popular_day}, Count:{popular_day_count}')

    # display the most common start hour
    popular_hour = df['start_hour'].mode()[0]
    popular_hour_count = df[df['start_hour'] == popular_hour].shape[0]
    print(f'Most popular start hour: {popular_hour}, Count:{popular_hour_count}')

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()
    
    # display most commonly used start station
    popular_start_station = df['Start Station'].mode()[0]
    popular_start_station_count = df[df['Start Station'] == popular_start_station].shape[0]
    print(f'Most popular start station: {popular_start_station}, Count:{popular_start_station_count}')

    # display most commonly used end station
    popular_end_station = df['End Station'].mode()[0]
    popular_end_station_count = df[df['End Station'] == popular_end_station].shape[0]
    print(f'Most popular end station: {popular_end_station}, Count:{popular_end_station_count}')

    # display most frequent combination of start station and end station trip
    popular_trip_tuple = (df['Start Station'] + ' -> ' + df['End Station']).value_counts().head(1)
    popular_trip = popular_trip_tuple.index[0]
    popular_trip_count = popular_trip_tuple.iloc[0]
    print(f'Most frequent combination of start station and end station trip: {popular_trip}, Count:{popular_trip_count}')

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # display travel time statistics
    total_duration = df['Trip Duration'].sum()
    total_duration_count = df['Trip Duration'].shape[0]
    total_duration_avg = df['Trip Duration'].mean()
    print(f'Total Duration:{total_duration}, Count:{total_duration_count}, Avg Duration:{total_duration_avg}')


    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # Display counts of user types
    total_users = df['User Type'].shape[0]
    subscriber_count = df[df['User Type'] == 'Subscriber'].shape[0]
    customer_count = df[df['User Type'] == 'Customer'].shape[0]
    print(f'Total Users: {total_users}')
    print(f'Subscribers:{subscriber_count}, Customers:{customer_count}')

    # Display counts of gender
    if filters.city.lower() != 'washington':
        male_count = df[df['Gender'] == 'Male'].shape[0]
        female_count = df[df['Gender'] == 'Female'].shape[0]
        not_specified_count = df['Gender'].isna().sum()

        print(f'Male:{male_count}, Female:{female_count}, Not Specified:{not_specified_count}')

        # Display earliest, most recent, and most common year of birth
        earliest_birth = df['Birth Year'].min()
        most_recent_birth = df['Birth Year'].max()
        birth_mode = df['Birth Year'].mode()[0]
        print(f'Earliest Birth:{earliest_birth}, Most recent:{most_recent_birth}, Most common year of birth:{birth_mode}')

    else:
        print('\nUnfortunately gender and birth information is not available for Washington.')

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def main():
    while True:
        # Filtering inputs
        get_filters()
        print(filters)

        # loading data
        try:
            df = load_data(filters)
        except:
            print('Unable to do run the program. Please have necessary csv files in the same folder with the program!')
            break
        else:
            time_stats(df)
            station_stats(df)
            trip_duration_stats(df)
            user_stats(df)

            chunksize = 5
            totalchunk = math.ceil(df.shape[0] / chunksize)
            i = 0
            while True:
                if i >= totalchunk:
                    break
                individual = input(f"\n{Fore.GREEN}Would you like to view individual trip data? Type 'yes' or 'no'{Style.RESET_ALL}\n")

                if (individual.lower() == 'no'):
                    break
                else:
                    print('\n')
                    i += 1
                    print(f'Chunk [{i}/{totalchunk}]')
                    df_json = df.iloc[i*chunksize:(i+1)*chunksize].to_json(orient='index')
                    json_dump = json.dumps(json.loads(df_json), indent=4)
                    print(json_dump)
                    print(f'End of Chunk [{i}/{totalchunk}]')
                    print('-'*40)
            restart = input(f'\n{Fore.GREEN}Would you like to restart? Enter yes or no.{Style.RESET_ALL}\n')
            if restart.lower() != 'yes':
                break


if __name__ == "__main__":
	main()