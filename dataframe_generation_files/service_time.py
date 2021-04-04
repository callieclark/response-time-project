from scipy.stats import lognorm
import numpy as np
import datetime as dt

def log_norm_service_time(df, average_time=23.2,s=0.18):
    #this function takes in the average time for CFS response and uses a lognormal
    #distribution to generate a srice time colum
    dist=lognorm.rvs(s, size=len(df),scale=1)*average_time
    service_time=[dt.timedelta(minutes = int(i)) for i in dist]
    df.loc[:,'Service Time']=service_time
    print('Stats of dist:','min',min(dist),'max', max(dist), 'mean',np.mean(dist))

    return df
