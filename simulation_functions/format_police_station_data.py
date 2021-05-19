import pandas as pd


def create_police_station_df(csv='Police_Stations_-_Map.csv',folder='Simulation_Data'):
    PS_data = pd.read_csv(folder+'/'+csv)
    PS_data['user_id']=1

    cr_lat=[]
    cr_long=[]

    for i in range(len(PS_data)):
        s = PS_data['LOCATION'][i]
        s= s[1:-1]
        f = [float(x) for x in s.split(", ")]
        cr_lat.append(f[0])
        cr_long.append(f[1])

    PS_data['lat']=cr_lat
    PS_data['long']=cr_long
    return PS_data, cr_lat,cr_long
