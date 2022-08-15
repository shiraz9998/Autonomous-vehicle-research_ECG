#pip install pandas
#pip install openpyxl
#pip install plotly
#pip install haversine

import pandas as pd
import numpy as np
import haversine as hs
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import sys
import tidy

#import csv


#Calculate the distance (in different units) between two points on the earth using their latitude and longitude.
def distanceHaversinePoints(p1_lat,p1_lng,p2_lat,p2_lng):
    loc1=(p1_lat,p1_lng)
    loc2=(p2_lat,p2_lng)
   #print(loc1, loc2)
    return hs.haversine(loc1,loc2,unit='m')
    
            
def distanceHaversineVectors(p1_lat,p1_lng,p2_lat,p2_lng):
    distance=[]
    for i in np.arange(len(p1_lat)):
        #print(p1_lat[i],p1_lng[i],p2_lat[i],p2_lng[i])
        dis=distanceHaversinePoints(p1_lat[i],p1_lng[i],p2_lat[i],p2_lng[i])
        distance.append(dis)
        #print(distance)
    return distance


def mergeEgoAndLeadVehicle (ego,lead) :
    if lead is not None:
        lead.rename(columns={"Latitude":"lead_Latitude"}, inplace=True)
        lead.rename(columns={"Longitude":"lead_Longitude"}, inplace=True)
        lead.rename(columns={"Speed":"lead_Speed"}, inplace=True) 
        lead.rename(columns={"Distance_Driven":"lead_Distance_Driven"}, inplace=True) 
        lead=lead[["SimulationTime","lead_Latitude","lead_Longitude","lead_Speed"]]
           
        merged = pd.merge(ego[["SimulationTime","Latitude","Longitude","Distance_Driven"]],lead,how='inner',on='SimulationTime')
        merged["DistanceToLead"]=distanceHaversineVectors(
            merged.lead_Latitude,
            merged.lead_Longitude,
            merged.Latitude,
            merged.Longitude
            )
        merged['CumulativeDistanceToLead']=np.cumsum(merged.DistanceToLead) #Return the cumulative sum of the elements along a given axis.
        merged['CumulativeDistanceToLeadPWR2']=np.cumsum(merged.DistanceToLead**2) 
        # X = merged.loc[:,['Latitude','Longitude']].values
        # y = merged.loc[:,'Distance_Driven'].values
        # gam = LinearGAM(n_splines=25).gridsearch(X, y)
        # X_lead = merged.loc[:,['lead_Latitude','lead_Longitude']].values
        # merged["PredictEgoDistance_Driven"]=gam.predict(X_lead)
        # merged['CumulativeDistanceToLeadV2']=np.cumsum(merged.DistanceToLead*merged["PredictEgoDistance_Driven"]>=merged["Distance_Driven"])        
        
    else:
        merged=ego
        merged['lead_Latitude']=None
        merged['lead_Longitude']=None
        merged['lead_Speed']=None
        merged['CumulativeDistanceToLead']=None
        merged['CumulativeDistanceToLeadPWR2']=None
        # merged['PredictEgoDistance_Driven']=None
        # merged['CumulativeDistanceToLeadV2']=None
    
        merged=merged[["SimulationTime","lead_Latitude","lead_Longitude","lead_Speed","CumulativeDistanceToLead","CumulativeDistanceToLeadPWR2"]]
    return merged


#Takinging the pathes we will need, it used an already make table that's called 'calc_simulator_and_corresponding_physiological_files.csv' 
# and should be in yours 'Readme' folder. This code takes only the relevant pathes.
CSV_ACC = pd.read_csv(r"C:\Users\WIN10\OneDrive\שולחן העבודה\WIN10\Research\Project\Ariel Uni\Readme\calc_simulator_and_corresponding_physiological_files.csv", skipinitialspace = True, encoding='latin-1')
ACC =  pd.DataFrame()
ACC = CSV_ACC #Convert the table with the paths to data frame

ACC = ACC[ACC['Scenario'] == 'ACC']
ACC = ACC.drop(["PhysiologicalFile","TobiFile", "TeleoperationFile", "KinematicFile", "triggered_by"], axis = 1) #Removing unwanted columns
ACC = ACC.dropna() #Remove missing entries
ACC.reset_index(drop=True, inplace=True) #reset to index
print(ACC)

#If your folder look like 'C:\Users\Shiraz\Desktop\project\data\Ariel Uni\A1_12345'
# You only should insert 'C:\Users\Shiraz\Desktop\project\data\Ariel Uni'
path = input('please enter the path of the main\'s folder that\'s contains all the users folders: ') #The path on my computer: C:\Users\WIN10\OneDrive\שולחן העבודה\WIN10\Research\Project\Ariel Uni
old_path = 'G:\My Drive\Ariel Uni'

#i = 0
#Replace the beginning of each path according to the location on your PC
#while i < len(ACC):
for i in range(len(ACC)):
    ACC.loc[i, 'SimulatorFile'] = ACC.loc[i,"SimulatorFile"].replace(old_path, path) #insert this val, to line num i and col 'SimulationTime'
    ACC.loc[i, 'GPSFile']       = ACC.loc[i,"GPSFile"].replace(old_path, path)        #insert this val, to line num i and col 'GPSFile'
    ACC.loc[i, 'PreprocessFile']= ACC.loc[i,"PreprocessFile"].replace(old_path, path) #insert this val, to line num i and col 'PreprocessFile'
    #i += 1 
print(ACC)



#Create a blank DF to collect the data into each time From the for loop
df = pd.DataFrame()
df_final = pd.DataFrame()
#df_merged_conncat = pd.DataFrame(columns=['Id', 'ACC','simulationTime', 'distance_for_lead', 'ECG_Rate',])


for i in range(len(ACC)):
    t_id  = ACC['Id'].iloc[i]
    t_acc = ACC['Condition'].iloc[i]
    path_dfECG  = str(ACC['PreprocessFile'].iloc[i])
    path_dfEgo  = str(ACC['SimulatorFile'].iloc[i])
    path_dfLead = str(ACC['GPSFile'].iloc[i])

    try:
        
        data_Ego = tidy.tidy_engine(path_dfEgo)
        data_Lead = tidy.tidy_gps(path_dfLead)
    
        if (data_Ego is not None) and  (data_Lead is not None):
            df_merged= mergeEgoAndLeadVehicle (data_Ego, data_Lead)
            df_merged = df_merged[['SimulationTime', "CumulativeDistanceToLead"]]
            df_merged = np.round(df_merged, decimals = 3)
            

            if path_dfECG is not None:
                path_dfECG = ACC.loc[i,"PreprocessFile"].replace(";", "_") #insert this val, to line num i and col 'PreprocessFile'
                data_preprocess = pd.read_csv(path_dfECG.strip("‪u202a"),  encoding='latin-1') 
                data_preprocess = data_preprocess.filter(items=['SimulationTime','ECG_Rate'])        
        
                data_preprocess.insert(0,"Id", t_id)
                data_preprocess.insert(1,'ACC', t_acc)
                data_preprocess = np.round(data_preprocess, decimals = 3)
                
            df = pd.merge(df_merged, data_preprocess, how='inner')
            df_final = df_final.append(df)
            
    except:
            e = sys.exc_info() #This function give information about the exception that is currently being handled
            print(i, e) 

#Create a column that shows the distance of the driver from the lead vehicle at all SimulationTime        
df_final['distanceDriverFromLead'] = df_final['CumulativeDistanceToLead'].diff()

df_final = df_final[["Id", "ACC","SimulationTime", "ECG_Rate", "CumulativeDistanceToLead", "distanceDriverFromLead" ]]
#df_final = df_final.sort_values('distanceDriverFromLead')
print(df_final)


#Creating graphs:
pio.renderers.default = 'browser' #Export of the graphs

#A graph that will show all the scenarios together:
plot_all_scenarios_together = px.scatter( y=df_final['ECG_Rate'], x=df_final['distanceDriverFromLead'],
                 color= df_final.ACC, width=10, height=10)
plot.show()

#A graph that will show all the scenarios separately:
plot_all_scenarios_separately = px.scatter(df_final, y=df_final['ECG_Rate'],
                              x=df_final['distanceDriverFromLead'],facet_col="ACC",  color= df_final.ACC,
                              width=10, height=10)            
plot_all.show()


#graph for each LOAD type:
DF_LOAD1 = pd.DataFrame()
DF_LOAD2 = pd.DataFrame()
DF_LOAD3 = pd.DataFrame()

DF_LOAD1= df_final.loc[df_final["ACC"].isin(["LOAD1_TTC1", "LOAD1_TTC2"])]
DF_LOAD2= df_final.loc[df_final["ACC"].isin(["LOAD2_TTC1", "LOAD2_TTC2"])]
DF_LOAD3= df_final.loc[df_final["ACC"].isin(["LOAD3_TTC1", "LOAD3_TTC2"])]

plot1 = px.scatter( y=DF_LOAD1['ECG_Rate'], x=DF_LOAD1['distanceDriverFromLead'], color= DF_LOAD1.ACC) 
plot2 = px.scatter( y=DF_LOAD2['ECG_Rate'], x=DF_LOAD2['distanceDriverFromLead'], color= DF_LOAD2.ACC)
plot3 = px.scatter( y=DF_LOAD3['ECG_Rate'], x=DF_LOAD3['distanceDriverFromLead'], color= DF_LOAD3.ACC)
          
plot1.show()
plot2.show()
plot3.show()

#df_final.to_csv('df_Prediction_finel_csv.csv', index= False, header='true')


        
      

