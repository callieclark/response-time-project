import pandas as pd
import numpy as np
import osmnx as ox

class Police:
    def __init__(self,ID,G,loc,resp,dt):
        self.ID=ID #a unique id
        self.G=G #pointer to the graph the officer travels on (Warning:edits to this graph have global consequences)
        self.loc=loc #the Node that the police officer is at
        self.resp=resp #true if the officer is responding to a crime event, false if patroling
        self.downtime=dt #Remaining time that the police is "down" due to a response event
        self.nodeInd=self.getNodeInd() #the index of the node that the officer is located in list(G.nodes())

    #tested
    #Randomly move the officer to an adjacent node if they are not responding
    def walk(self):
        if not(self.resp):
            wk= list(nx.classes.function.all_neighbors(self.G,(list(self.G.nodes)[self.nodeInd])))
            j = np.random.choice(wk)
            self.updateLoc(j)

    #moves the police officer toward the node they need to respond to
    def respond(self):
        if self.resp:
            return

    #updates the police location (no matter if they are responding or patroling)
    def update(self):
        i.walk()
        i.respond()

    #updates the location of the officer to the new Node (and changes the node ID)
    def updateLoc(self,newloc):
        self.loc=newloc
        self.nodeInd=self.getNodeInd()

    #gets the index of the node that corresponds to its ID
    def getNodeInd(self):
        return list(self.G.nodes).index(self.loc)


def create_pc_node(PS_data,G,Gs,cr_lat,cr_long):
    PC_node=[]
    Police_officers=[]

    for i in range(len(PS_data)):
        t = (ox.get_nearest_node(Gs, (cr_lat[i], cr_long[i])))
        PC_node.append(t)

    for i in range(len(PC_node)):
        Pol_loc=PC_node[i]
        Police_officers.append(Police(i,G,Pol_loc,False,0))

    return PC_node,Police_officers
