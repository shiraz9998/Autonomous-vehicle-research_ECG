#pip install neurokit2
#pip install pandas
#pip install openpyxl
#pip install plotly

import numpy as np
#import neurokit2 as nk
import pandas as pd
from openpyxl import Workbook
wb = Workbook()
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import sys

#'simulation time' from Data_Frame, 'SimulationTime' from data_calc_events 
def merge_df(df1,df_calc):
    #merged_cut = pd.merge(df1, df_calc, on=['Id', 'Latency'], how='inner') 
    merged_cut = pd.merge(df1, df_calc, how='inner') 
    df_details_cut = merged_cut[merged_cut['simulation_time']< merged_cut['SimulationTime']]
    return df_details_cut


#Latency is a file called calc.events.csv from the Readme folder from Ariel Uni Drive.
data_calc_events = pd.read_csv('C:/Users/WIN10/OneDrive/שולחן העבודה/WIN10/Research/Project/Participants/StatisticalAnalyses/calc_events.csv')
data_calc_events = data_calc_events[data_calc_events.Scenario == 'Latency'] #take from Latency just the Scenario whose name is Latency
data_calc_events = data_calc_events[['Id', 'SimulationTime', 'Event_Name','Condition']]

dataECG = pd.read_excel('C:/Users/WIN10/OneDrive/שולחן העבודה/WIN10/Research/Project/ECG/data_ecg_latency_preprocess.xlsx')

#Create a blank DF to collect the data into each time From the for loop
df_details_final = pd.DataFrame(columns=['Id', 'Latency','simulation_time', 'HRV_HF' ])


for i in range(len(dataECG)):
   
    t_id = dataECG['Id'].iloc[i]
    t_latency = dataECG['Latency'].iloc[i]
    dfECG = str(dataECG ['preprocess'].iloc[i])
    
    try:
        data_all = pd.read_csv(dfECG.strip("‪u202a")) #‪u202a=blank character therefore remove it
        data_all = data_all[['SimulationTime','ECG_Rate_Mean','HRV_SDNN', 'HRV_LF','HRV_HF','ECG_Rate']] 
        data_all.rename(columns={"SimulationTime": "simulation_time"}, inplace=True)    
        data_all.insert(0,"Id", t_id)
        data_all.insert(1,'Latency', t_latency)

        print(i)
    except:
        e = sys.exc_info() #This function give information about the exception that is currently being handled
        print(i, e)
    
    t_data_calc_events = ( data_calc_events [data_calc_events.Id == t_id ])
    t_data_calc_events = ( t_data_calc_events[t_data_calc_events.Condition == t_latency] )

    # Cutting data_calc_events by 'Lead vehicle at the end of the curve V2'
    t_data_calc_events = t_data_calc_events[(t_data_calc_events.Event_Name =='Lead vehicle at the end of the curve V2')]
    
    #Using the merge_df function that appears at the beginning of the code. 
    df_details_cut_ECG = merge_df(data_all, t_data_calc_events)
    df_details_cut_ECG = df_details_cut_ECG.filter(items=['Id', 'Latency', 'simulation_time', 'HRV_HF'])
    df_details_final = pd.concat([df_details_cut_ECG, df_details_final], ignore_index=True)

    #Sorting the data df_details_final on the arrangement of the simulation_time column according to size
    df_details_final = df_details_final.sort_values('simulation_time')
print(df_details_final)
#df_details_final.to_csv('df_details_final_csv1.csv', index= False, header='true')


window = 200
df_details_final['Moving_Avg_HRV_HF']=None
df_details_final.loc[df_details_final['Latency']=='Latency1','Moving_Avg_HRV_HF'] = df_details_final[df_details_final['Latency']=='Latency1'].HRV_HF.rolling(window).mean()
df_details_final.loc[df_details_final['Latency']=='Latency2','Moving_Avg_HRV_HF'] = df_details_final[df_details_final['Latency']=='Latency2'].HRV_HF.rolling(window).mean()
df_details_final.loc[df_details_final['Latency']=='Latency3','Moving_Avg_HRV_HF'] = df_details_final[df_details_final['Latency']=='Latency3'].HRV_HF.rolling(window).mean()


#pio.renderers.default = 'browser'
ECG_plot = px.line(df_details_final, y='Moving_Avg_HRV_HF', x='simulation_time', color= df_details_final.Latency)
ECG_plot.show()
