#pip install neurokit2
#pip install pandas
#pip install openpyxl

import numpy as np
import neurokit2 as nk
import pandas as pd
from openpyxl import Workbook
wb = Workbook()

#returns DataFrame with: ECG_R_Peaks
#data, info = nk.bio_process(ecg=data_all["ECG"], sampling_rate=512)
data_all = pd.read_excel('C:/Users/WIN10/OneDrive/שולחן העבודה/WIN10/Research/Project/g.techAmp Data of A5_316544_Slalom_2_far at (12;39;46).xlsx')
 
#Per second there are 512 samples, and we want to take data every time_window seconds
#   and that's a lot of data, so we'll take the data every 512 * time_window seconds.

time_window=40 #for example time_window=40 sec
sampling_rate=512
steps=40 #create a new epoch every "step" second
    

#returns DataFrame with: ECG_R_Peaks
data, info = nk.ecg_process(data_all["ECG"], sampling_rate=sampling_rate)


#returns a dict containing DataFrames for all epochs with: ECG_R_Peaks
epochs= nk.epochs_create(data,  
                         events= np.arange(start=0, 
                                           stop=len(data_all), 
                                           step=sampling_rate*steps),
                         sampling_rate=sampling_rate,
                         epochs_start=0, 
                         epochs_end=time_window)   

#returns DataFrame with:ECG_Rate_Mean, HRV LF, HRV HF, ECG_HRV
intervalrelated= nk.ecg_intervalrelated(epochs,sampling_rate=sampling_rate)

#returns DataFrame with: Event_Onset, ECG_Rate_SD
eventrelated= nk.ecg_eventrelated(epochs)


df_eventrelated    = eventrelated[['Event_Onset', 'ECG_Rate_SD']]
df_intervalrelated = intervalrelated[['ECG_Rate_Mean','HRV_SDNN', 'HRV_LF','HRV_HF']]

Data_Frame = pd.concat([ df_eventrelated, df_intervalrelated], axis=1)

#heart rate= (1/ rate mean)*60
Data_Frame.reset_index(drop=True, inplace=True) #reset to index


#we will go line by line in Data_Frame, so that each time we take from data_all
# only the columns 'measurement time', 'simulation time' Whose row index is the current Data_Frame.Event_Onset value
df_measuremen_time = data_all.iloc[Data_Frame.Event_Onset][['measurement time', 'simulation time' ]]
df_measuremen_time.reset_index(drop=True, inplace=True) #reset to index

# Place the DataFrames side by side
Data_Frame = pd.concat([Data_Frame, df_measuremen_time], axis=1)

 
print(Data_Frame)




