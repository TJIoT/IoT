import csv
from datetime import datetime,timedelta
import sys
import json
import pandas as pd
import numpy as np

class SubscribeChoice:
    Temperture=1
    Pressure=1
    Humidity=1
    Date=1
    Filename="recieveData.csv"
    MaxNum=100
    count=0
    DataSet=[['Month', 'Day','Hour','Humidity', 'Temperture', 'Pressure']]

    def __init__(self,Temperture=1,Pressure=1,Humidity=1,Date=1,Filename="recieveData.csv",MaxNum=3):
        self.Temperture=Temperture
        self.Pressure=Pressure
        self.Humidity=Humidity
        self.Date=Date
        self.Filename=Filename
        self.MaxNum=MaxNum
        self.count=0
         

    def add_data(self,items):
        a=Time(items)
        self.DataSet.append([a.month,a.day,a.hour,items['CurrentHumidity']['value'],items['CurrentTemperature']['value'],items['CurrentPressure']['value']])
        self.count+=1
        if(self.count==self.MaxNum):
             self.write_to_file()
             sys.exit()

    def write_to_file(self):
        self.DataSet.print()
        with open(self.Filename, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(self.DataSet)

        with open(self.Filename) as f:
	        print(f.read())

class Time:
     year=0
     month=0
     day=0
     hour=0
     def __init__(self,items):
        data = items['DetectTime']['value']
        timestamp=float(data)/1000
        utc_datetime=datetime.utcfromtimestamp(timestamp)
        cst_datetime=utc_datetime+timedelta(hours=8)
        #print(cst_datetime)
        self.year=cst_datetime.year
        self.month=cst_datetime.month
        self.day=cst_datetime.day
        self.hour=cst_datetime.hour

data = pd.read_csv('merged_data.csv', header=None)
data = data.dropna(axis=0, how='any')
data = np.array(data.iloc[1:,:])
DataSet=[['Month', 'Day','Hour','Humidity', 'Temperture', 'Pressure']]
time= data[:, 0]  # 时间
num = data.shape[0]


def time_to_timestamp(time_str):
    dt_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    return int(dt_obj.timestamp()) * 1000

for i in range(num):
    items=time_to_timestamp(time[i])
    timestamp=float(items)/1000
    utc_datetime=datetime.utcfromtimestamp(timestamp)
    cst_datetime=utc_datetime+timedelta(hours=8)
    #print(cst_datetime)
    year=cst_datetime.year
    month=cst_datetime.month
    day=cst_datetime.day
    hour=cst_datetime.hour
    DataSet.append([month,day,hour,data[i][1],data[i][2],data[i][3]])


      

with open('tran_data.csv', 'w',newline='') as file:
    writer = csv.writer(file)
    writer.writerows(DataSet)

