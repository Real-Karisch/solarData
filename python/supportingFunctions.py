import pandas as pd
import numpy as np
import re

#### STORAGE SIZE AND SYSTEM SIZE ####

#function to generate subset of dataframe based on regex pattern for a given column
#inputs:
#   df: the dataframe to be subset
#   col: string, name of the column for regex match
#   pattern: string, regex pattern to match
#   ignorecase: boolean, if true ignore case in regex match
#outputs a dataframe that is a subset of input dataset
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

### these functions subset the data for the given inverter manufacturer
#input is a dataframe to be subset
#outputs a subset dataframe
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

#function to generate a subset for all other inverter manufacturers besides those listed above
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

#function to generate sums of storage and system sizes for the data for a particular subset based on a subset function (defined above)
#inputs:
#   df: dataframe to find sums
#   filterFn: a function that subsets the dataframe before summing
#outputs a list containing two lists (for storage and system size) of three sums each corresponding to residential, commercial and industrial sectors
def simpleIndiv(df, filterFn):
    subset = filterFn(df)

    residentialDF = subset[subset['sector'] == 'Residential']
    commercialDF = subset[subset['sector'] == 'Commercial']
    industrialDF = subset[subset['sector'] == 'Industrial']

    systemSizeResSum = residentialDF['systemSizeDC'].sum()
    systemSizeComSum = commercialDF['systemSizeDC'].sum()
    systemSizeIndSum = industrialDF['systemSizeDC'].sum()

    storageSizeResSum = residentialDF['storageSize'].sum()
    storageSizeComSum = commercialDF['storageSize'].sum()
    storageSizeIndSum = industrialDF['storageSize'].sum()

    return [[systemSizeResSum, systemSizeComSum, systemSizeIndSum], [storageSizeResSum, storageSizeComSum, storageSizeIndSum]]

#function to append the monthly sums to the residential, commercial and industrial lists within the storage size and system size dictionaries
#inputs:
#   dict: dictionary (either storage or system size) holding the monthly time series lists for each sector
#   sums: list with three items for the three sectors
#   key: string, key of company of the sums
#outputs the dictionary with the new sums appended
def dictAppend(dict, sums, key):
    dict[key]['residential'].append(sums[0])
    dict[key]['commercial'].append(sums[1])
    dict[key]['industrial'].append(sums[2])

    return dict

#function that generates a monthly time series csv from a storage or system size dictionary
#inputs:
#   dict: a dictionary with three sector time series lists for each inverter manufacturer
#   filename: string for name of file to be output
def simpleCsv(dict, filename):
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other'] #inverter manufacturers
    sectors = ['residential', 'commercial', 'industrial'] #market sectors

    startingDate = pd.to_datetime('2013-12-31')

    index = []

    #loop to generate index names (months) for the output csv
    for i in range(len(dict[mans[0]][sectors[0]])):
        index.append(startingDate + pd.tseries.offsets.MonthEnd(i + 1))

    outDF = pd.DataFrame(index = index)

    #loop to populate dataframe with time series data for each inverter manufacturer for each sector
    for man in mans:
        for sector in sectors:
            col = man + '_' + sector #column names based on manufacturer and sector separated by underscore

            outDF[col] = dict[man][sector]

    path = './../outputs/' + filename #output in 'outputs' folder

    outDF.to_csv(path)

#function to generate the system and storage size time series csv's from a given full dataset
#inputs:
#   df: full solar dataset
#   numMonths: number of months after January 2014
def simpleMaster(df, numMonths):
    df = df[df['systemSizeDC'].notna()] 
    df['storageSize'].fillna(0, inplace = True) #fill null values in storage size with zeros

    startingDate = pd.to_datetime('2013-12-31')

    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other'] #inverter manufacturers
    fns = [solarEdgeFilter, enphaseFilter, smaFilter, froniusFilter, sunPowerFilter, apsFilter, deltaFilter, ginlongFilter, otherFilter] #subset functions corresponding to each inverter manufacturer

    systemSizeDict = {}
    storageSizeDict = {}

    #loop to create storage and system size dictionaries with keys for each manufacturer
    for man in mans:
        systemSizeDict[man] = {'residential': [], 'commercial': [], 'industrial': []}
        storageSizeDict[man] = {'residential': [], 'commercial': [], 'industrial': []}
    
    #loop to subset the data by month
    for i in range(numMonths):
        priorMonth = startingDate + pd.tseries.offsets.MonthEnd(i)
        activeMonth = startingDate + pd.tseries.offsets.MonthEnd(i + 1)

        activeSubset = df[pd.to_datetime(df['appDate']) > priorMonth]
        activeSubset = activeSubset[pd.to_datetime(activeSubset['appDate']) <= activeMonth]

        #loop to find monthly sums for each manufacturer and sector, and populate the dictionaries
        for j in range(len(mans)):
            [systemSizeSums, storageSizeSums] = simpleIndiv(activeSubset, fns[j])
            systemSizeDict = dictAppend(systemSizeDict, systemSizeSums, mans[j])
            storageSizeDict = dictAppend(storageSizeDict, storageSizeSums, mans[j])

    #generate csv's  
    simpleCsv(systemSizeDict, 'systemSize.csv')
    simpleCsv(storageSizeDict, 'storageSize.csv')

#### INSTALLER CSV ####

#functions to filter data for the given installer (operate like manufacturer filter functions defined above)

def sunrunFilter(df):
    pattern = 'sun ?run'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def vivintFilter(df):
    pattern = 'vivint'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def freedomforeverFilter(df):
    pattern = 'freed(om|in) ?forever'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def solarcityFilter(df):
    pattern = 'solar ?city|tesla'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def sunpowerFilter(df):
    pattern = '^sun ?power'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def petersenFilter(df):
    pattern = 'peters[eo]n ?dean'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def sungevityFilter(df):
    pattern = 'sungevity'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def semperFilter(df):
    pattern = 'semper ?solaris'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def solciusFilter(df):
    pattern = 'solcius'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def brightplanetFilter(df):
    pattern = 'bright ?planet'

    df = reFilter(df, 'installer', pattern, ignorecase = True)

    return df

def otherInstFilter(df):
    patterns = ['sun ?run','vivint','freed(om|in) ?forever','solar ?city|tesla','^sun ?power','peters[eo]n ?dean','sungevity','semper ?solaris','solcius','bright ?planet']

    otherInd = []

    for i in df.index:
        installer = df.loc[i, 'installer']

        otherFlag = True
        for pattern in patterns:
            search = re.search(pattern, installer, re.IGNORECASE)
            if search is not None:
                otherFlag = False
                break

        if otherFlag:
            otherInd.append(i)

    df = df.loc[otherInd]

    return df

#like dictAppend function defined above, but using installers -> manufacturers instead of manufacturers -> sector
def instDictAppend(dict, sums, instKey, manKeys):
    for i in range(len(sums)):
        dict[instKey][manKeys[i]].append(sums[i])

    return dict

#like simpleIndiv function defined above, but using installers -> manufacturers instead of manufacturers -> sector
def instIndiv(df, instFilterFn, manFilterFns):
    subset = instFilterFn(df)

    sums = []
    
    for manFilterFn in manFilterFns:
        active = manFilterFn(subset)

        sums.append(active['systemSizeDC'].sum())

    return sums

#like simpleCsv function defined above, but using installers -> manufacturers instead of manufacturers -> sector
def instCsv(dict, filename):
    installers = ['sunrun','vivint','freedomforever','solarcity','sunpower','petersen','sungevity','semper','solcius','brightplanet','other']
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']

    startingDate = pd.to_datetime('2013-12-31')

    index = []

    for i in range(len(dict[installers[0]][mans[0]])):
        index.append(startingDate + pd.tseries.offsets.MonthEnd(i + 1))

    outDF = pd.DataFrame(index = index)

    for installer in installers:
        for man in mans:
            col = installer + '_' + man

            outDF[col] = dict[installer][man]

    path = './../outputs/' + filename

    outDF.to_csv(path)

#like simpleMaster function defined above, but using installers -> manufacturers instead of manufacturers -> sector
def instMaster(df, numMonths):
    df = df[df['installer'].notna()]

    startingDate = pd.to_datetime('2013-12-31')

    installers = ['sunrun','vivint','freedomforever','solarcity','sunpower','petersen','sungevity','semper','solcius','brightplanet','other']
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']

    instFns = [sunrunFilter,vivintFilter,freedomforeverFilter,solarcityFilter,sunpowerFilter,petersenFilter,sungevityFilter,semperFilter,solciusFilter,brightplanetFilter,otherInstFilter]
    manFns = [solarEdgeFilter, enphaseFilter, smaFilter, froniusFilter, sunPowerFilter, apsFilter, deltaFilter, ginlongFilter, otherFilter]

    outDict = {}

    for inst in installers:
        outDict[inst] = {}
        for man in mans:
            outDict[inst][man] = []
    
    for i in range(numMonths):
        priorMonth = startingDate + pd.tseries.offsets.MonthEnd(i)
        activeMonth = startingDate + pd.tseries.offsets.MonthEnd(i + 1)

        activeSubset = df[pd.to_datetime(df['appDate']) > priorMonth]
        activeSubset = activeSubset[pd.to_datetime(activeSubset['appDate']) <= activeMonth]
        for j in range(len(installers)):
            activeSums = instIndiv(activeSubset, instFns[j], manFns)
            outDict = instDictAppend(outDict, activeSums, installers[j], mans)

    instCsv(outDict, 'installers.csv')

#### THIRD PARTY OWNER CSV ####

#these functions are just like the installer functions above, but using third parties instead of installers

def sunrunTpFilter(df):
    pattern = 'sun ?run'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def vivintTpFilter(df):
    pattern = 'vivint'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def freedomforeverTpFilter(df):
    pattern = 'freed(om|in) ?forever'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def solarcityTpFilter(df):
    pattern = 'solar ?city|tesla'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def sunpowerTpFilter(df):
    pattern = '^sun ?power'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def sunnovaTpFilter(df):
    pattern = 'sunn?ova'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def sungevityTpFilter(df):
    pattern = 'sungevity'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def semperTpFilter(df):
    pattern = 'semper ?solaris'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def solciusTpFilter(df):
    pattern = 'solcius'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def brightplanetTpFilter(df):
    pattern = 'bright ?planet'

    df = reFilter(df, 'thirdParty', pattern, ignorecase = True)

    return df

def otherTpFilter(df):
    patterns = ['sun ?run','vivint','freed(om|in) ?forever','solar ?city|tesla','^sun ?power','sunn?ova','sungevity','semper ?solaris','solcius','bright ?planet']

    otherInd = []

    for i in df.index:
        installer = df.loc[i, 'thirdParty']

        otherFlag = True
        for pattern in patterns:
            search = re.search(pattern, installer, re.IGNORECASE)
            if search is not None:
                otherFlag = False
                break

        if otherFlag:
            otherInd.append(i)

    df = df.loc[otherInd]

    return df

def tpCsv(dict, filename):
    installers = ['sunrun','vivint','freedomforever','solarcity','sunpower','sunnova','sungevity','semper','solcius','brightplanet','other']
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']

    startingDate = pd.to_datetime('2013-12-31')

    index = []

    for i in range(len(dict[installers[0]][mans[0]])):
        index.append(startingDate + pd.tseries.offsets.MonthEnd(i + 1))

    outDF = pd.DataFrame(index = index)

    for installer in installers:
        for man in mans:
            col = installer + '_' + man

            outDF[col] = dict[installer][man]

    path = './../outputs/' + filename

    outDF.to_csv(path)

def tpMaster(df, numMonths):
    df = df[df['installer'].notna()]

    startingDate = pd.to_datetime('2013-12-31')

    installers = ['sunrun','vivint','freedomforever','solarcity','sunpower','sunnova','sungevity','semper','solcius','brightplanet','other']
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']

    instFns = [sunrunTpFilter,vivintTpFilter,freedomforeverTpFilter,solarcityTpFilter,sunpowerTpFilter,sunnovaTpFilter,sungevityTpFilter,semperTpFilter,solciusTpFilter,brightplanetTpFilter,otherTpFilter]
    manFns = [solarEdgeFilter, enphaseFilter, smaFilter, froniusFilter, sunPowerFilter, apsFilter, deltaFilter, ginlongFilter, otherFilter]

    outDict = {}

    for inst in installers:
        outDict[inst] = {}
        for man in mans:
            outDict[inst][man] = []
    
    for i in range(numMonths):
        priorMonth = startingDate + pd.tseries.offsets.MonthEnd(i)
        activeMonth = startingDate + pd.tseries.offsets.MonthEnd(i + 1)

        activeSubset = df[pd.to_datetime(df['appDate']) > priorMonth]
        activeSubset = activeSubset[pd.to_datetime(activeSubset['appDate']) <= activeMonth]
        for j in range(len(installers)):
            activeSums = instIndiv(activeSubset, instFns[j], manFns)
            outDict = instDictAppend(outDict, activeSums, installers[j], mans)

    tpCsv(outDict, 'tpinstallers.csv')