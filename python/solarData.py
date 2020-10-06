import pandas as pd
import numpy as np
import re
import os
from supportingFunctions import *

import time

start = time.time()

NUMMONTHS = 78

os.chdir('/home/karisch/programming/projects/solar/python')

pgeRaw = pd.read_csv('./../data/PGE_Interconnected_Applications_Dataset_2020-06-30.csv')
sceRaw = pd.read_csv('./../data/SCE_Interconnected_Applications_Dataset_2020-06-30.csv')
sdgeRaw = pd.read_csv('./../data/SDGE_Interconnected_Applications_Dataset_2020-06-30.csv')

cols = ['Technology Type','System Size DC','Storage Size (kW AC)','App Approved Date','Customer Sector','Installer Name','Inverter Manufacturer 1','Third Party Owned','Third Party Name']
colsShort = ['techType','systemSizeDC','storageSize','appDate','sector','installer','invMan','thirdPartyBool','thirdParty']

allData = pd.concat([pgeRaw[cols][:-1], sceRaw[cols][:-1], sdgeRaw[cols][:-1]])

allData.columns = colsShort

allData = allData[allData['techType'].notna()]
allData = allData[allData['invMan'].notna()]

allData.reset_index(inplace=True, drop=True)

solarPvInd = []

for i in list(allData.index):

    checkStr = allData.loc[i, 'techType']
    search = re.search('Solar PV|SOLAR PV', checkStr)
    if search is not None:
        solarPvInd.append(i)

allData = allData.loc[solarPvInd]
allData = allData[allData['appDate'] >= '2014-01-01']

allData.reset_index(inplace=True, drop=True)

resData = allData[allData['sector'] == 'Residential']
resData = resData[resData['installer'].notna()]
resData.reset_index(inplace=True, drop=True)

tpData = resData[resData['thirdParty'].notna()]
tpData.reset_index(inplace=True, drop=True)

simpleMaster(allData, numMonths = NUMMONTHS)
instMaster(resData, numMonths = NUMMONTHS)
tpMaster(tpData, numMonths=NUMMONTHS)

end = time.time()

print(end - start)