
import pandas as pd
import osmnx as ox
from shapely.geometry import Point
from datetime import datetime

def format_data(csv,folder='Chicago_Data/Daily_Profiles'):
    #t0 is a fromatted string with the date of the day passed in
    data = pd.read_csv(folder+'/'+csv)
    data['user_id']=1

    data['Timestamp']=pd.to_datetime(data['Timestamp']).dt.tz_localize(None)
    # if len(data['Timestamp'].dt.date.unique())==1:
    #     t0=(data['Timestamp'].dt.date.unique()[0]).strftime('%Y-%m-%d %H:%M:%S')
    # else:
    #     print("More Data than one day is passed in, only first day evaluated")
    #     t0=(data['Timestamp'].dt.date.unique()[0]).strftime('%Y-%m-%d %H:%M:%S')
    data['Timestamp']=data['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return data



def create_groups(data, grouping):
    if grouping=='Violent':
        print('Groups are Violent and Non-violent')
        prop = data.groupby(['Priority']).get_group(2)
        non_index = data.groupby(['Priority']).get_group(3)


        frames = [prop, non_index]
        result = pd.concat(frames,sort='True')

        Group1 = data.groupby(['Priority']).get_group(1)#Violent
        Group2 = result.sort_index(axis=0)#Nonviolent

    elif grouping=='Index':
        print('Groups are Index and Non-index')

        Violent = data.groupby(['Priority']).get_group(1)
        prop = data.groupby(['Priority']).get_group(2)
        result = pd.concat([Violent,prop],sort='True')
        Group1=result.sort_index(axis=0)
        Group2=data.groupby(['Priority']).get_group(3)

    else:
        print('ERROR in Specification')

    Group1 = Group1.reset_index()
    Group2 = Group2.reset_index()

    return Group1,Group2

def create_crime_dfs(csv, grouping,folder='Chicago_Data/Daily_Profiles'):
    data=format_data(csv,folder='Chicago_Data/Daily_Profiles')
    data=data[[ 'Timestamp','Latitude', 'Longitude','Priority','Service Time', '#Units']]
    if grouping!='BAU':
        Group1,Group2=create_groups(data, grouping)
        Group1=Group1[[ 'Timestamp','Latitude', 'Longitude','Priority','Service Time', '#Units']]
        Group2=Group2[[ 'Timestamp','Latitude', 'Longitude','Priority','Service Time','#Units']]
    elif grouping=='BAU':
        print('BAU: No Groupings')
        Group1='not specified'
        Group2='not specified'
    else:
        Print('incorrect grouping')

    return data,Group1,Group2


def get_nearest_crime_node(crime_data,Gs):
    crime_node=[]
    crime_geo=[]
    for i in range(len(crime_data)):
        t = (ox.get_nearest_node(Gs, (crime_data['Latitude'][i], crime_data['Longitude'][i])))
        x = Point(crime_data['Longitude'][i],crime_data['Latitude'][i])
        crime_geo.append(x)
        crime_node.append(t)

    return crime_node,crime_geo


def create_time_sequence(crime_data):
    datetime_object=[]
    time_seq=[]
    srvtime_object=[]
    ser_time =[]

    crime_data['Timestamp']=pd.to_datetime(crime_data['Timestamp']).dt.tz_localize(None)
    if len(crime_data['Timestamp'].dt.date.unique())==1:
        t0=(crime_data['Timestamp'].dt.date.unique()[0]).strftime('%Y-%m-%d %H:%M:%S')
    else:
        print("More Data than one day is passed in, only first day evaluated")
        t0=(crime_data['Timestamp'].dt.date.unique()[0]).strftime('%Y-%m-%d %H:%M:%S')
    crime_data['Timestamp']=crime_data['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    print('Day Evaluating: ',t0)

    t_ini = datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
    s0 ='00:00:00'
    ss_ini = datetime.strptime(s0, '%H:%M:%S')

    for i in range(len(crime_data)):
        datetime_str = crime_data['Timestamp'][i]
        datetime_object.append(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S'))
        tt = (datetime_object[i]-t_ini).total_seconds()
        time_seq.append(tt)

        srvtime_str = crime_data['Service Time'][i]
        srvtime_object.append(datetime.strptime(srvtime_str[7:-1],'%H:%M:%S'))
        ss = (srvtime_object[i]-ss_ini).total_seconds()
        ser_time.append(ss)


        time_min = [x / 60 for x in time_seq]
        ser_min = [x / 60 for x in ser_time]

    num_units = crime_data['#Units'].values.tolist()

    return time_min,ser_min, num_units
