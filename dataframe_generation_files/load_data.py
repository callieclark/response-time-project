import pandas as pd
import zipfile
def format_file(zip_file,csv_file, timezone='UTC',timestamp_col='Date'):
    #This function reads the csv in the zip
    #and takes in the timezone and column with time information and standardizes the timestamp
    #Chicago timezone is "America/Chicago"
    #TODO make this more robust for various types of files

    with zipfile.ZipFile(zip_file) as z:
        with z.open(csv_file) as f:
            df = pd.read_csv(f)

    #df=pd.read_csv(csv_file)
    df.dropna(axis=0,inplace=True) #drop rows with all NAN values
    df.loc[:,'Timestamp']=pd.to_datetime(df[timestamp_col]).dt.tz_localize(timezone,nonexistent='shift_forward',ambiguous='NaT')
    df.loc[:,'Date']=pd.to_datetime(df[timestamp_col]).dt.date

    return df
