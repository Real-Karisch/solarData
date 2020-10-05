import pandas as pd
import numpy as np
import re

def reFilter(df, col, pattern, ignorecase = False):
    ind = []
    for i in list(df.index):
        checkStr = df.loc[i, col]
        if ignorecase:
            search = re.search(pattern, checkStr, re.IGNORECASE)
        else:
            search = re.search(pattern, checkStr)
        if search is not None:
            ind.append(i)

    df = df.loc[ind]

    return df

def solarEdgeFilter(df):
    pattern = 'solar ?edge'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def enphaseFilter(df):
    pattern = 'enphase'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def smaFilter(df):
    pattern = 'sma'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def froniusFilter(df):
    pattern = 'fronius'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def sunPowerFilter(df):
    pattern = 'sunpower'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def apsFilter(df):
    pattern = 'ap[s ]'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def deltaFilter(df):
    pattern = 'delta'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def ginlongFilter(df):
    pattern = 'ginlong'

    df = reFilter(df, 'invMan', pattern, ignorecase = True)

    return df

def otherFilter(df):
    patterns = ['solar ?edge', 'enphase', 'sma', 'fronius', 'sunpower', 'ap[s ]', 'delta', 'ginlong']

    otherInd = []

    for i in list(df.index):
        checkStr = df.loc[i, 'invMan']

        otherFlag = True

        for pattern in patterns:
            if re.search(pattern, checkStr, re.IGNORECASE) is not None:
                otherFlag = False
                break
        
        if otherFlag:
            otherInd.append(i)

    df = df.loc[otherInd]

    return df

def systemSizeIndiv(df, filterFn):
    subset = filterFn(df)

    residentialDF = subset[subset['sector'] == 'Residential']
    commercialDF = subset[subset['sector'] == 'Commercial']
    industrialDF = subset[subset['sector'] == 'Industrial']

    residentialSum = residentialDF['systemSizeDC'].sum()
    commercialSum = commercialDF['systemSizeDC'].sum()
    industrialSum = industrialDF['systemSizeDC'].sum()

    return [residentialSum, commercialSum, industrialSum]

def dictAppend(dict, sums, key):
    dict[key]['residential'].append(sums[0])
    dict[key]['commercial'].append(sums[1])
    dict[key]['industrial'].append(sums[2])

    return dict

def systemSizeCsv(dict):
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']
    sectors = ['residential', 'commercial', 'industrial']

    #header = pd.MultiIndex.from_product([mans, sectors])

    startingDate = pd.to_datetime('2013-12-31')

    index = []

    for i in range(len(dict[mans[0]][sectors[0]])):
        index.append(startingDate + pd.tseries.offsets.MonthEnd(i + 1))

    #outDF = pd.DataFrame(index = index, columns = header)

    outDF = pd.DataFrame(index = index)
    
    for man in mans:
        for sector in sectors:
            col = man + '_' + sector

            outDF[col] = dict[man][sector]

    outDF.to_csv('./../outputs/systemSize.csv')

def systemSizeMaster(df, numMonths):
    df = df[df['systemSizeDC'].notna()]

    startingDate = pd.to_datetime('2013-12-31')

    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']
    fns = [solarEdgeFilter, enphaseFilter, smaFilter, froniusFilter, sunPowerFilter, apsFilter, deltaFilter, ginlongFilter, otherFilter]

    outDict = {}

    for man in mans:
        outDict[man] = {'residential': [], 'commercial': [], 'industrial': []}
 
    for i in range(numMonths):
        priorMonth = startingDate + pd.tseries.offsets.MonthEnd(i)
        activeMonth = startingDate + pd.tseries.offsets.MonthEnd(i + 1)

        activeSubset = df[pd.to_datetime(df['appDate']) > priorMonth]
        activeSubset = activeSubset[pd.to_datetime(activeSubset['appDate']) <= activeMonth]

        for j in range(len(mans)):
            activeSums = systemSizeIndiv(activeSubset, fns[j])
            outDict = dictAppend(outDict, activeSums, mans[j])
        
    systemSizeCsv(outDict)