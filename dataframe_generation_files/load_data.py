import pandas as pd
def format_file(csv_file, timezone='UTC',timestamp_col='Date'):
    #This function reads the csv
    #and takes in the timezone and column with time information and standardizes the timestamp
    #Chicago timezone is "America/Chicago"
    df=pd.read_csv(csv_file)
    df.dropna(axis=0,inplace=True) #drop rows with all NAN values
    df.loc[:,'Timestamp']=pd.to_datetime(df[timestamp_col]).dt.tz_localize(timezone,nonexistent='shift_forward',ambiguous='NaT')
    df.loc[:,'Date']=pd.to_datetime(df[timestamp_col]).dt.date

    return df
