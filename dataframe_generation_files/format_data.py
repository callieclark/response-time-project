import pandas as pd
def check_lat_long(df):
    #This function checks that latitude and longitude are specified
    #To Do: add functionality to self specify colum names and re-assign
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        print('Data has Latitude and Longitude')
    else:
        print('Data does not have Latitude and Longitude')
        print ('Data has', df.columns)

violent_crime=["01A",'02','03','04A','04B']
property_crime=['05','06','07','09']
index_crime=["01A",'02','03','04A','04B','05','06','07','09']
nonindex_crime=['01B', '08A', '08B','10','11','12','13','14','15','16','17','18','19','20','22','24','26']
nonviolent_crime=nonindex_crime+property_crime
ucr_labels={'08B':'Simple Battery', '02':'Criminal Sexiual Assault', '06':'Larceny', '11':'Fraud', '26':'Misc Non-Index',
            '05':'Burglary', '20':'Offenses Against Family', '17':'Criminal Sexual Abuse', '14':'Vandalism', '16':'Prostitution',
            '08A':'Simple Assault',
       '03':'Robbery', '18':'Drug Abuse', '07':'Motor Vehicle Theft', '10':'Forgery & Counterfeiting', '15':'Weapons Violation', '01A': 'Homicide',
            '12':'Embezzlement', '09':'Arson', '04B':'Aggravated Battery', '13':'Stolen Property',
       '04A':'Aggravated Assault', '24':'Disorderly Conduct', '22':'Liquor License', '19':'Gambling', '01B':'Involuntary Manslaughter'}

def classify_response_type(df, crime_responder='Police', crime_types=violent_crime, UCRcol='FBI Code' ):
    #this function takes in the type of responder and the crimes they should respond to, and assumes all
    #other  CFS are responded by the other type of responder. It produces a column with (0,1) indicator
    #showing if the police should respond (1) for each CFS
    if crime_responder=='Police':
        df.loc[:,'Police']=df[UCRcol].isin(crime_types)*1
    if crime_responder=='Alternative':
        df.loc[:,'Police']=(~df[UCRcol].isin(crime_types))*1

    return df

UCR_dict={"01A":1,'02':1,'03':1,'04A':1,'04B':1,\
'05':2,'06':2,'07':2,'09':2, \
'01B':3, '08A':3, '08B':3,'10':3,'11':3,'12':3,'13':3,'14':3,'15':3,'16':3,'17':3,'18':3,'19':3,'20':3,'22':3,'24':3,'26':3}

def set_priority(df, map_dict=UCR_dict, code_col='FBI Code'):
    #this function assigns a priority to each CFS usign the UCR code
    #1:Violent crime, 2: non-violent index crime, 3: non-index crime
    df['Priority']=df[code_col].map(map_dict)

    return df

def set_number_responders(df,number_per_call=2):
    #This function creates a new column and sets the number of responders for each CFS.
    #Right now the number is constant for all situations, but functionality can be added to change that
    df.loc[:,'#Responders']=number_per_call
    return df
