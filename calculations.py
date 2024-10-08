import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf 
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns
import statistics
import tkinter


def filter_trading_days(data, start_date, end_date):
    data = data[data.index.weekday < 5]

    # Fetch the NYSE calendar (you can adjust this based on your market)
    nyse = mcal.get_calendar('NYSE')

    # Valid days argument needs ot be in string format instead of an object
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # print(nyse.tz.zone)
    valid_trading_days = nyse.valid_days(start_date=start_date_str, end_date=end_date_str, tz='America/New_York')

     # Convert valid_trading_days to a list (if it's a single Timestamp, wrap it in a list)
    if isinstance(valid_trading_days, pd.Timestamp):
        valid_trading_days = [valid_trading_days]

    # Convert valid_trading_days to a DatetimeIndex for comparison valid trading days is a list of timestamp objects, so can't compare in the isin() function
    valid_trading_days_index = pd.DatetimeIndex(valid_trading_days)

    if data.index.freq is None:  # Likely daily data
        data = data[data.index.normalize().isin(valid_trading_days_index)]
    else:  # Likely intraday data
        # Convert to just dates (dropping time part) for filtering
        data_dates = data.index.normalize()
        data = data[data_dates.isin(valid_trading_days_index)]

    return data

def calculate_avg_dr(data):
    # Need to exclude today's data from both datasets to ensure intraday data and data use same dates
    data = data[data.index.date < pd.Timestamp.today().date()].copy()

    # STUDY THIS LINE, LIST COMPREHENSION, THIS VS 4 LINES OF CODE
    daily_ranges = pd.Series([high - low for high, low in zip(data['High'], data['Low'])])

    avg_dr = round(daily_ranges.mean(), 2)
    return avg_dr, daily_ranges

def calculate_avg_dr_by_day(data):
    data.loc[:, 'Daily_Range'] = data['High'] - data['Low']
    data.loc[:, 'Day_of_Week'] = data.index.day_name()

    dr_by_day = data.groupby('Day_of_Week')['Daily_Range']
    avg_dr_by_day = round(dr_by_day.mean(), 2)
    return avg_dr_by_day, dr_by_day

def calculate_avg_intraday_range(intraday_data):
     # Need to exclude today's data from both datasets to ensure intraday data and data use same dates
    intraday_data = intraday_data[intraday_data.index.date < pd.Timestamp.today().date()].copy()

    # loc[] syAllows u to acces and modify rows and columns using their labels. similar to iloc which is index location
    # The code below basically means all rows, within the intraday_range column will be set to the data highs and lows
    # intraday_data.loc[:, 'Intraday_Range'] = intraday_data['High'] - intraday_data['Low']
    # intraday_data.loc[:, 'Day_of_Week'] = intraday_data.index.day_name()

    # Group by the date and calculate the AM range become more comfy w lambda
    intraday_ranges = intraday_data.groupby(intraday_data.index.date).apply(
    lambda x: round(x['High'].max() - x['Low'].min(), 2)
    )

    avg_intraday_range = intraday_ranges.mean()
    return intraday_data, avg_intraday_range, intraday_ranges

def calculate_avg_intraday_range_by_day(intraday_data, data):
    intraday_ranges_df = data.copy()
    intraday_ranges_df['Day_of_Week'] = intraday_ranges_df.index.day_name()

    intraday_ranges = intraday_data.groupby(intraday_data.index.date).apply(
    lambda x: round(x['High'].max() - x['Low'].min(), 2)
    )
   
   # CHAT GPT did this line make sure you understand what reindex does
    intraday_ranges_df['Intraday_Range'] = intraday_ranges.reindex(intraday_ranges_df.index.date).values
   
    intraday_range_by_day = intraday_ranges_df.groupby('Day_of_Week')['Intraday_Range']
    avg_intraday_range_by_day = intraday_range_by_day.mean()
    return avg_intraday_range_by_day, intraday_range_by_day

def calculate_median_dr(daily_ranges):

    median_dr = round(daily_ranges.median(), 2)
    print(f'This is the median dr: {median_dr}')
    return median_dr

def calculate_median_dr_by_day(dr_by_day):
    median_dr_by_day = round(dr_by_day.median(), 2)
    print(f'Here is the median dr by day : {median_dr_by_day}')
    return median_dr_by_day

def calculate_median_intraday_range(intraday_ranges):
    median_intraday_range = round(intraday_ranges.median(), 2)
    print(f'This si the median intraday range: {median_intraday_range}')
    return median_intraday_range

def calculate_median_intraday_range_by_day(intraday_range_by_day):
   median_intraday_range_by_day = round(intraday_range_by_day.median(), 2)
   print(f'This si the median intraday range by day: {median_intraday_range_by_day}')
   return median_intraday_range_by_day

def calculate_median_bearish_reversal_time(data):
    # GPT did this for me, make sure you understand all if it and can do it yourself before moving on. 
     # Convert Time_of_High and Time_of_Low to datetime
    data['Time_of_High'] = pd.to_datetime(data['Time_of_High'], format='%H:%M:%S').dt.time
    data['Time_of_Low'] = pd.to_datetime(data['Time_of_Low'], format='%H:%M:%S').dt.time

    # Define bearish days as those where Time_of_Low is after Time_of_High
    bearish_days = data[data['Opening_Price'] > data['Closing_Price']]

    # Calculate the average time of the high on bearish days
    if not bearish_days.empty:
        # Convert time to seconds since midnight
        time_in_seconds = bearish_days['Time_of_High'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second)
        
        # Calculate the average time in seconds
        median_seconds = time_in_seconds.median()
        
        # Convert average seconds back to time
        median_time_of_high = pd.to_datetime(median_seconds, unit='s').time()
        print(f"\n The MEDIAN time of the high on bearish days is: {median_time_of_high}")
        return median_time_of_high
    else:
        print("No bearish days found in the given data.")
        return None
def calculate_median_bullish_reversal_time(data):
    # CHAT GPT ran this function for me, make sure i understand and can do pit myself before moving on.
     # Convert Time_of_High and Time_of_Low to datetime
    data['Time_of_High'] = pd.to_datetime(data['Time_of_High'], format='%H:%M:%S').dt.time
    data['Time_of_Low'] = pd.to_datetime(data['Time_of_Low'], format='%H:%M:%S').dt.time

    # Define bullish days as those where Time_of_High is after Time_of_Low
    bullish_days = data[data['Closing_Price'] > data['Opening_Price']]

    # Calculate the average time of the low on bullish days
    if not bullish_days.empty:
        # Convert time to seconds since midnight
        time_in_seconds = bullish_days['Time_of_Low'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second)
        
        # Calculate the average time in seconds
        median_seconds = time_in_seconds.median()
        
        # Convert average seconds back to time
        median_time_of_low = pd.to_datetime(median_seconds, unit='s').time()
        
        print(f"The MEDIAN time of the low on bullish days is: {median_time_of_low}")
        return median_time_of_low
    else:
        print("No bullish days found in the given data.")
        return None