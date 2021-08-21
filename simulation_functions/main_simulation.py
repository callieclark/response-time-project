import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon
import osmnx as ox
import fiona
import networkx as nx


class ndk:
    G=[]
    nodes=[]
    SPL={}
    def calc():
        for i in ndk.nodes:
            ndk.SPL[i]=nx.shortest_path_length(ndk.G, source=i, weight='time')
    def shortest_path_length(G, source, target, weight='none'):
        return ndk.SPL[source][target]

def set_ndk(Gs,PC_node):
    ndk.G=Gs
    ndk.nodes=PC_node
    ndk.calc()
    return ndk

def column(matrix, i):
    return [row[i] for row in matrix]

def dispatch_logic(polys, pt):
    #pass in geometry shape of crime, determines which police district it is in
    dis_t=0
    ## for loop to check that the point lies in which polygon
    for x in range(len(polys)):
        if pt.within(polys['geometry'][x]):
            dis_t= polys['dist_num'][x]
            dis_node = polys['node'][x]
            dis_Off = polys['NoOfOfficers'][x]

            break


    ## if the point is outside the polygons and the point is approximated to the closest polygon

    if dis_t not in polys['dist_num'].values:
        dd = 1000000;
        for x in range(len(polys)):
            t1  = polys['geometry'][x]
            t = gpd.GeoSeries(t1)
            t.crs = 4326

            t2 = gpd.GeoSeries([pt])
            t2.crs = 4326

            dist = t.distance(t2)

            if (dist <= dd).bool():
                dd = dist
                dis_t = polys['dist_num'][x]
                dis_node = polys['node'][x]
                dis_Off = polys['NoOfOfficers'][x]

    return (dis_t,dis_node,dis_Off)

def create_polys(PS_data,Gs,shp='Chicago_PB.shp',folder='Simulation_Data'):
    multipol = fiona.open(folder+'/'+shp)
    multi= multipol.next()
    polys  = gpd.read_file(folder+'/'+shp)

    ## This is to change the 3 police beat which are basically water to closest beat which is land
    polys['dist_num'][2] = '16'
    polys['dist_num'][3] = '16'
    polys['dist_num'][7] = '22'

    geometry =[Point (xy) for xy in zip(PS_data['long'],PS_data['lat'])]
    #geo_df = gpd.GeoDataFrame(PS_data,geometry = geometry)

    ## Pre-assigning the Police station node to polys
    polys['node']=1
    for x in range(len(polys)):
        dis_t= polys['dist_num'][x]
        te = PS_data[PS_data['DISTRICT'] == dis_t]
        trr = (ox.get_nearest_node(Gs, (te['lat'].values[0], te['long'].values[0])))
        polys['node'][x]=trr

        #eventually functionalize this so csv is an input

    police_staffing=pd.read_csv('Simulation_Data/PoliceBeat_staffing.csv',index_col='assigned_district').drop(columns=['Unnamed: 0'])
    police_staffing.index=police_staffing.index.astype(str)
    polys=polys.merge(police_staffing[['#Officers']],how='left',left_on='dist_num',right_index=True)
    polys['NoOfOfficers']=round((polys['#Officers']/5)*0.75*0.60) #5 assumes officers work 40hr weeks
    #0.75 of patrolling officers are patrolling and only 60% of time should be public cfs (from paper)

    return polys


def eva_resp_time(police,Crime,percent_operating,ndk,polys,Gs):
    Officers_maxed_out=0
    Resp_time = []
    orig_node = police # node number for all police stations
    #officer_demand=[[] for j in range(len(orig_node))]
    officer_demand= {k: [] for k in polys['dist_num'].values }
    time_list=[]
    tot_officer_demand=[]

    my_array=[]
    arr_crime = [[0 for i in range(2)] for j in range(len(orig_node))]
    my_array = np.array(arr_crime).astype('int64')
    my_array[:,1]= orig_node
    PC_stalk = [[0 for i in range(9)] for j in range(len(orig_node))]

    ## PC_stalk is the main list which is keeping track of all police station node.
    # PC_stalk stores the assigned crime to a police station along with when was the crime assigned , its service time,the crimes being actively handled , crimes in waiting queue because of officers unavailability


    for x in range(len(orig_node)):
        PC_stalk[x][0] =orig_node[x] #creates list for each police station node, and assigns value as first object
    for x in range(len(orig_node)):
        for y in range(3,9):
            PC_stalk[x][y]=[]
    columnIndex = 0
    # ('PC_stalk',PC_stalk)
    for j in range(len(Crime[0])): #loops through every cfs in the day
        #dest_node = Crime[1][j]
        Crime_node = Crime[1][j]
        Crime_time = Crime[0][j]
        Ser_time = Crime[2][j]
        num_units = Crime[4][j] #number of units that respond to the crime
        if j !=len(Crime[0])-1:
            Crime_time_next = Crime[0][j+1]#ask Chitra what this does


        ## Assign the crime node to police node by calling the dispatch logic

        pt = Crime[3][j] #assigns shapely point to pt
        dist_no,s,NoOff= dispatch_logic(polys, pt) #returns dis_t,dis_node,dis_Off (district #, police node, #officers)
        idx = np.argwhere(column(PC_stalk, 0) == s)[0][0] #idx is the police station index number
        NoOff=round((NoOff*percent_operating)/2) #transforms from # officers into units
        if NoOff<1:
            NoOff=1
            print(percent_operating,' % Reduction returns number less than one for district ',dist_no)
            print('Rounded up to 1 unit')

        # if PC_stalk[idx][1] >= NoOff:
        #     Officers_maxed_out+=1

        counter=0
        while num_units > 0:
            #PC_stalk[idx][1] is the number of officers dispatched
            if PC_stalk[idx][1] < NoOff:  # if the officer are available : assign crime as active
                    PC_stalk[idx][1]= PC_stalk[idx][1]+1
                    #need to figure out how to remove the right number below
                    #PC_stalk[idx][1]= PC_stalk[idx][1]+Crime[4][j] #add multiple units here
                    PC_stalk[idx][3].append(Crime_time)
                    PC_stalk[idx][4].append(Crime_node)
                    temp = ndk.shortest_path_length(Gs, PC_stalk[idx][0], Crime_node, weight='time')
                    PC_stalk[idx][5].append(2*temp + Crime_time + Ser_time)
                    Resp_time.append([temp,Crime_time])


            else : #-->  if officers are already occupied make a waiting queue for all the crimes being assinged
                if counter==0:
                    Officers_maxed_out+=1
                PC_stalk[idx][2]= PC_stalk[idx][2]+1
                PC_stalk[idx][6].append(Crime_node)
                PC_stalk[idx][7].append(Crime_time)
                PC_stalk[idx][8].append(Ser_time)

            num_units=num_units-1
            counter+=1




        if j !=len(Crime[0])-1: #this loop updates queue during simulation
            ## Check if a PC node is going to available
            for statn in range(len(orig_node)): #check statn vs idx
                y=0
                while (PC_stalk[statn][1])>0 and y<=PC_stalk[statn][1]-1:
                    if PC_stalk[statn][5][y] <= Crime_time_next: #if crime has been served
                        if PC_stalk[statn][2]>0: #if there are cfs in the queue
                            PC_stalk[statn][2]= PC_stalk[statn][2]-1
                            temp1 = PC_stalk[statn][5][y]
                            PC_stalk[statn][3].remove(PC_stalk[statn][3][y])
                            PC_stalk[statn][3].append(temp1)
                            temp2 = PC_stalk[statn][6][0]     ##Change from y to 0
                            PC_stalk[statn][4].remove(PC_stalk[statn][4][y])
                            PC_stalk[statn][4].append(temp2)
                            temp3 = ndk.shortest_path_length(Gs, PC_stalk[statn][0],temp2, weight='time')
                            wait = temp1 - PC_stalk[statn][7][0]
                            se_time = PC_stalk[statn][8][0]
                            PC_stalk[statn][5].remove(PC_stalk[statn][5][y])
                            PC_stalk[statn][5].append(2*temp3 + temp1 + se_time)
                            Resp_time.append([wait+temp3,PC_stalk[statn][7][0]])
                            PC_stalk[statn][6].remove(PC_stalk[statn][6][0])
                            PC_stalk[statn][7].remove(PC_stalk[statn][7][0])
                            PC_stalk[statn][8].remove(PC_stalk[statn][8][0])
                        else:
                            PC_stalk[statn][1]= PC_stalk[statn][1]-1 #remove officer from active queue
                            #PC_stalk[idx][1]= PC_stalk[idx][1]-Crime[4][j]
                            PC_stalk[statn][3].remove(PC_stalk[statn][3][y])
                            PC_stalk[statn][4].remove(PC_stalk[statn][4][y])
                            PC_stalk[statn][5].remove(PC_stalk[statn][5][y])
                    else:
                        y=y+1


        officer_demand[dist_no].append((Crime_time,PC_stalk[idx][1]+PC_stalk[idx][2]))
        time_list.append(Crime_time)
        tot_officer_demand.append(np.sum([PC_stalk[i][1]+PC_stalk[i][2] for i in range(len(orig_node))]))
        #add sum of all PC_stalk[idx][1] over index to to_list
        #add number seconds to list

    d=[]

    # The for loop below processes leftovers when all crimes have been served

    for idx in range(len(orig_node)): #
        while PC_stalk[idx][2]>0:
            #print ('idx',idx,'PC',PC_stalk[idx])
            a = min(PC_stalk[idx][5]) # is earliest time of finishing call
            ind = PC_stalk[idx][5].index(a)
            PC_stalk[idx][2]= PC_stalk[idx][2]-1
            temp1 = PC_stalk[idx][5][ind]
            PC_stalk[idx][3].remove(PC_stalk[idx][3][ind])
            PC_stalk[idx][3].append(temp1)
            temp2 = PC_stalk[idx][6][0]
            PC_stalk[idx][4].remove(PC_stalk[idx][4][ind])
            PC_stalk[idx][4].append(temp2)
            temp3 = ndk.shortest_path_length(Gs, PC_stalk[idx][0],temp2, weight='time')
            wait = temp1 - PC_stalk[idx][7][0]
            ser_time = PC_stalk[idx][8][0]
            PC_stalk[idx][5].remove(PC_stalk[idx][5][ind])
            PC_stalk[idx][5].append(2*temp3 + temp1 + ser_time)
            d.append([wait+temp3,PC_stalk[idx][7][0]])
            PC_stalk[idx][6].remove(PC_stalk[idx][6][0])
            PC_stalk[idx][7].remove(PC_stalk[idx][7][0])
            PC_stalk[idx][8].remove(PC_stalk[idx][8][0])
    Resp_time.extend(d) #does this capture all the wait times?

    return Resp_time,Officers_maxed_out, officer_demand,time_list, tot_officer_demand
