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

def dictAppend(dict, sums, key):
    dict[key]['residential'].append(sums[0])
    dict[key]['commercial'].append(sums[1])
    dict[key]['industrial'].append(sums[2])

    return dict

def simpleCsv(dict, filename):
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']
    sectors = ['residential', 'commercial', 'industrial']

    startingDate = pd.to_datetime('2013-12-31')

    index = []

    for i in range(len(dict[mans[0]][sectors[0]])):
        index.append(startingDate + pd.tseries.offsets.MonthEnd(i + 1))

    outDF = pd.DataFrame(index = index)

    for man in mans:
        for sector in sectors:
            col = man + '_' + sector

            outDF[col] = dict[man][sector]

    path = './../outputs/' + filename

    outDF.to_csv(path)

def simpleMaster(df, numMonths):
    df = df[df['systemSizeDC'].notna()]
    df['storageSize'].fillna(0, inplace = True)

    startingDate = pd.to_datetime('2013-12-31')

    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']
    fns = [solarEdgeFilter, enphaseFilter, smaFilter, froniusFilter, sunPowerFilter, apsFilter, deltaFilter, ginlongFilter, otherFilter]

    systemSizeDict = {}
    storageSizeDict = {}

    for man in mans:
        systemSizeDict[man] = {'residential': [], 'commercial': [], 'industrial': []}
        storageSizeDict[man] = {'residential': [], 'commercial': [], 'industrial': []}
 
    for i in range(numMonths):
        priorMonth = startingDate + pd.tseries.offsets.MonthEnd(i)
        activeMonth = startingDate + pd.tseries.offsets.MonthEnd(i + 1)

        activeSubset = df[pd.to_datetime(df['appDate']) > priorMonth]
        activeSubset = activeSubset[pd.to_datetime(activeSubset['appDate']) <= activeMonth]

        for j in range(len(mans)):
            [systemSizeSums, storageSizeSums] = simpleIndiv(activeSubset, fns[j])
            systemSizeDict = dictAppend(systemSizeDict, systemSizeSums, mans[j])
            storageSizeDict = dictAppend(storageSizeDict, storageSizeSums, mans[j])
        
    simpleCsv(systemSizeDict, 'systemSize.csv')
    simpleCsv(storageSizeDict, 'storageSize.csv')

##################################################################################

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

def instDictAppend(dict, sums, instKey, manKeys):
    for i in range(len(sums)):
        dict[instKey][manKeys[i]].append(sums[i])

    return dict

def instIndiv(df, instFilterFn, manFilterFns):
    subset = instFilterFn(df)

    sums = []
    
    for manFilterFn in manFilterFns:
        active = manFilterFn(subset)

        sums.append(active['systemSizeDC'].sum())

    return sums

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

##############################################################################

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

def petersenTpFilter(df):
    pattern = 'peters[eo]n ?dean'

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
    patterns = ['sun ?run','vivint','freed(om|in) ?forever','solar ?city|tesla','^sun ?power','peters[eo]n ?dean','sungevity','semper ?solaris','solcius','bright ?planet']

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

def tpMaster(df, numMonths):
    df = df[df['installer'].notna()]

    startingDate = pd.to_datetime('2013-12-31')

    installers = ['sunrun','vivint','freedomforever','solarcity','sunpower','petersen','sungevity','semper','solcius','brightplanet','other']
    mans = ['solaredge','enphase','sma','fronius','sunpower','aps','delta','ginlong','other']

    instFns = [sunrunTpFilter,vivintTpFilter,freedomforeverTpFilter,solarcityTpFilter,sunpowerTpFilter,petersenTpFilter,sungevityTpFilter,semperTpFilter,solciusTpFilter,brightplanetTpFilter,otherTpFilter]
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

    instCsv(outDict, 'tpinstallers.csv')