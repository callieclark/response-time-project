import pandas as pd
import random
import datetime as dt
#test comment
def create_map(dates,season_map):
    #this function takes in dates and an empty dictionary and maps each date to a season
    for i in range(len(dates)):
        date=dates[i]
        year = date.year
        if dt.date(year, 3, 20) <= date <=dt.date(year, 6, 19):
            season_map[date]='spring'
        elif dt.date(year, 6, 20) <= date <=dt.date(year, 9, 21):
            season_map[date]='summer'
        elif dt.date(year, 9, 22) <= date <= dt.date(year, 12, 20):
            season_map[date]='fall'
        else:
            season_map[date]='winter'

    return season_map

def create_seasons(df,season_map):
    #this function takes in dates and an empty season map, and maps each CFS date to a
    #season and creates a new column
    season_map=create_map(df['Date'].unique(),season_map)
    df['season'] = df['Date'].map(season_map)
    return df

def calculate_frequency(df,groupon='Date'):
    #this function calculates the number of CFS in each day and creates a new column
    frequency_map=df[['Police','Date']].groupby(groupon).count().to_dict()['Police']
    df['Frequency']=df['Date'].map(frequency_map)
    return df

def calculate_quantiles(df, col='Frequency',quantile_list=[0.25,0.50,0.75,0.95]):
    #this function takes the column and quantile list passed in a returns a dataframe with the quantiles
    frequency_quantiles=df[[col]].quantile(quantile_list)
    return frequency_quantiles


def quantile_daily_profiles(df, daily_profiles,quantiles=[0.25,0.50,0.75,0.95],iterations=1,label='all_data'):
    #this function takes in the df, a profile dict and a quantile list and
    #populates the daily profile dict with date(s) for each quantile
    frequency_quantiles=calculate_quantiles(df, col='Frequency',quantile_list=quantiles)
    for i in quantiles:
        k=0
        date_list=[]
        upper=(frequency_quantiles.loc[i,]+frequency_quantiles.loc[i,]*0.01).values[0]
        lower=(frequency_quantiles.loc[i,]-frequency_quantiles.loc[i,]*0.01).values[0]
        dates=df[(df['Frequency']<upper) & (df['Frequency']>lower)].Date.unique()
        for j in range(iterations):
            random.seed(k)
            indexer=random.randint(0, len(dates)-1)
            date_list.append(dates[indexer])
            k+=1
        daily_profiles[label+'_'+str(i)]=date_list
    return daily_profiles

def worst_case_profiles(df, daily_profiles,number_profiles=3,label='all_data'):
    #this function takes in the df, a profile dict and number of days and
    #populates the daily profile dict with date(s) of the worst case day in the df
    daily_freq= df[['Date','Frequency']].sort_values(by='Frequency',ascending=False).drop_duplicates(subset=['Date'])
    if number_profiles==1:
        daily_profiles[label+'_worst_case']=[daily_freq['Date'].to_list()[0]]

    else:
        daily_profiles[label+'_worst_case']=daily_freq['Date'].to_list()[0:number_profiles]
    return daily_profiles

def generate_seasonal_profiles(df,seasonal_profiles,quantile_list=[0.5],iterations=1, number_profiles=1):
    #this function generates a dictionary with dates for each season of the specified quantiles and worst case days
    df_summer=df[df['season']=='summer']
    df_fall=df[df['season']=='fall']
    df_spring=df[df['season']=='spring']
    df_winter=df[df['season']=='winter']
    season_dict={'summer':df_summer,'fall':df_fall,'spring':df_spring,'winter':df_winter}

    for j in season_dict.keys():
        seasonal_profiles=quantile_daily_profiles(season_dict[j], seasonal_profiles,quantile_list,iterations,label=str(j))

    for j in season_dict.keys():
        seasonal_profiles=worst_case_profiles(season_dict[j],seasonal_profiles, number_profiles,label=str(j))

    return seasonal_profiles


def create_csv(daily_profiles,df,folder):
    #this function takes in the profile dictionary, df and desired folder and creates csvs for each date specified
    for i in daily_profiles.keys():
        for j in range(len(daily_profiles[i])):
            df_temp=df[df['Date']==daily_profiles[i][j]]
            _temp=df_temp[['Timestamp','Latitude','Longitude','#Units','Police','Priority','Service Time']].set_index('Timestamp').sort_index()
            _temp.to_csv(folder+'/'+str(i)+'_'+str(j)+'_timestamp.csv')
