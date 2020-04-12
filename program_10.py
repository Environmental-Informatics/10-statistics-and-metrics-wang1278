#!/bin/env python
# Modified on April 10, 2020
#  by Linji Wang
# Created on March 25, 2020
#  by Keith Cherkauer
#
# This script servesa as the solution set for assignment-10 on descriptive
# statistics and environmental informatics.  See the assignment documention 
# and repository at:
# https://github.com/Environmental-Informatics/assignment-10.git for more
# details about the assignment.
#
import pandas as pd
import scipy.stats as stats

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    # remove negative values
    DataDF=DataDF[~(DataDF['Discharge']<0)]
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    # clip the dataframe with the given date range
    DataDF=DataDF[startDate:endDate]
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    return( DataDF, MissingValues )

def CalcTqmean(Qvalues):
    """This function computes the Tqmean of a series of data, typically
       a 1 year time series of streamflow, after filtering out NoData
       values.  Tqmean is the fraction of time that daily streamflow
       exceeds mean streamflow for each year. Tqmean is based on the
       duration rather than the volume of streamflow. The routine returns
       the Tqmean value for the given data array."""
    # drop nodata values
    Qvalues = Qvalues.dropna()
    # calculate total time
    T=len(Qvalues)
    # calculate Tqmean
    Tqmean=(Qvalues>Qvalues.mean()).sum()/T
    return ( Tqmean )

def CalcRBindex(Qvalues):
    """This function computes the Richards-Baker Flashiness Index
       (R-B Index) of an array of values, typically a 1 year time
       series of streamflow, after filtering out the NoData values.
       The index is calculated by dividing the sum of the absolute
       values of day-to-day changes in daily discharge volumes
       (pathlength) by total discharge volumes for each year. The
       routine returns the RBindex value for the given data array."""
    # drop nodata values
    Qvalues = Qvalues.dropna()
    # calculate sum of absolute of day-to-day streamflow difference
    sum_abs = 0.0    
    for i in range(len(Qvalues)-1):
        sum_abs += abs(Qvalues[i+1]-Qvalues[i])
    # calculate R-B Index
    RBindex = (sum_abs/Qvalues.sum())
    return ( RBindex )

def Calc7Q(Qvalues):
    """This function computes the seven day low flow of an array of 
       values, typically a 1 year time series of streamflow, after 
       filtering out the NoData values. The index is calculated by 
       computing a 7-day moving average for the annual dataset, and 
       picking the lowest average flow in any 7-day period during
       that year.  The routine returns the 7Q (7-day low flow) value
       for the given data array."""
    # remove nodata values
    Qvalues = Qvalues.dropna()

    # find lowest average flow in any 7-day period
    val7Q = Qvalues.rolling(window=7).mean().min()
    return ( val7Q )

def CalcExceed3TimesMedian(Qvalues):
    """This function computes the number of days with flows greater 
       than 3 times the annual median flow. The index is calculated by 
       computing the median flow from the given dataset (or using the value
       provided) and then counting the number of days with flow greater than 
       3 times that value.   The routine returns the count of events greater 
       than 3 times the median annual flow value for the given data array."""
    # remove nodata values
    Qvalues = Qvalues.dropna()
    # computes the number of days with flows greater than 3x annual median flow
    median3x=(Qvalues>3*Qvalues.median()).sum()
    return ( median3x )

def GetAnnualStatistics(DataDF):
    """This function calculates annual descriptive statistcs and metrics for 
    the given streamflow time series.  Values are retuned as a dataframe of
    annual values for each water year.  Water year, as defined by the USGS,
    starts on October 1."""
    # column names
    colNames=['site_no','Mean Flow','Peak Flow','Median','Coeff Var','Skew','TQmean','R-B Index','7Q','3xMedian']
    # year range
    WYrange = range(1970,2020)
    # define a new dataframe to store annual metric values
    WYDataDF = pd.DataFrame(0.0, index=WYrange, columns=colNames)
    # define the index as Water Year
    WYDataDF.index.name = 'Water Year'
    # calculate the metrics for each water year   
    WYDataDF['site_no'] = DataDF['site_no'][0]
    for WY in WYrange:
        WYDataDF.loc[WY,'Mean Flow'] = DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"].mean()
        WYDataDF.loc[WY,'Peak Flow'] = DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"].max()
        WYDataDF.loc[WY,'Median'] = DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"].median()
        WYDataDF.loc[WY,'Coeff Var'] = DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"].std()/WYDataDF.loc[WY,'Mean Flow']*100
        WYDataDF.loc[WY,'Skew'] = stats.skew(DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"])
        WYDataDF.loc[WY,'TQmean'] = CalcTqmean(DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"])
        WYDataDF.loc[WY,'R-B Index'] = CalcRBindex(DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"])
        WYDataDF.loc[WY,'7Q'] = Calc7Q(DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"])
        WYDataDF.loc[WY,'3xMedian'] = CalcExceed3TimesMedian(DataDF['Discharge'][str(WY-1)+"-10-01":str(WY)+"-09-30"])        
    WYDataDF.index = DataDF.resample('AS-OCT').mean().index
    return ( WYDataDF )

def GetMonthlyStatistics(DataDF):
    """This function calculates monthly descriptive statistics and metrics 
    for the given streamflow time series.  Values are returned as a dataframe
    of monthly values for each year."""
    # column names
    colNames=['site_no','Mean Flow','Coeff Var','TQmean','R-B Index']
    # resample
    index = DataDF.resample('MS').mean().index
    # define a new dataframe to store monthly metric values
    MoDataDF = pd.DataFrame(0.0, index=index, columns=colNames)
    # define the index as Month
    MoDataDF.index.name = 'Month'
    # calculate the metrics for each month
    MoDataDF['site_no'] = DataDF['site_no'][0]
    MoDataDF['Mean Flow'] = DataDF['Discharge'].resample("MS").mean().values
    MoDataDF['Coeff Var'] = DataDF['Discharge'].resample("MS").std().values/MoDataDF['Mean Flow']*100
    MoDataDF['TQmean'] = DataDF['Discharge'].resample("MS").apply(CalcTqmean).values
    MoDataDF['R-B Index'] = DataDF['Discharge'].resample("MS").apply(CalcRBindex).values
    return ( MoDataDF )

def GetAnnualAverages(WYDataDF):
    """This function calculates annual average values for all statistics and
    metrics.  The routine returns an array of mean values for each metric
    in the original dataframe."""
    AnnualAverages=WYDataDF.mean(axis=0)
    return( AnnualAverages )

def GetMonthlyAverages(MoDataDF):
    """This function calculates annual average monthly values for all 
    statistics and metrics.  The routine returns an array of mean values 
    for each metric in the original dataframe."""
    # calculate mean for each month by grouping
    Mo_index=lambda x:x.month
    MonthlyAverages = MoDataDF.groupby(Mo_index).mean()
    MonthlyAverages.index.name = 'Date'
    return( MonthlyAverages )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define filenames as a dictionary
    # NOTE - you could include more than jsut the filename in a dictionary, 
    #  such as full name of the river or gaging site, units, etc. that would
    #  be used later in the program, like when plotting the data.
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    # define blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    MissingValues = {}
    WYDataDF = {}
    MoDataDF = {}
    AnnualAverages = {}
    MonthlyAverages = {}
    
    # process input datasets
    for file in fileName.keys():
        
        print( "\n", "="*50, "\n  Working on {} \n".format(file), "="*50, "\n" )
        
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
        print( "-"*50, "\n\nRaw data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # clip to consistent period
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '1969-10-01', '2019-09-30' )
        print( "-"*50, "\n\nSelected period data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # calculate descriptive statistics for each water year
        WYDataDF[file] = GetAnnualStatistics(DataDF[file])
        
        # calcualte the annual average for each stistic or metric
        AnnualAverages[file] = GetAnnualAverages(WYDataDF[file])
        
        print("-"*50, "\n\nSummary of water year metrics...\n\n", WYDataDF[file].describe(), "\n\nAnnual water year averages...\n\n", AnnualAverages[file])

        # calculate descriptive statistics for each month
        MoDataDF[file] = GetMonthlyStatistics(DataDF[file])

        # calculate the annual averages for each statistics on a monthly basis
        MonthlyAverages[file] = GetMonthlyAverages(MoDataDF[file])
        
        print("-"*50, "\n\nSummary of monthly metrics...\n\n", MoDataDF[file].describe(), "\n\nAnnual Monthly Averages...\n\n", MonthlyAverages[file])

        # add a column for river names as Station and output annual to .csv
        WYDataDF[file].insert(0,'Station',file)
        WYDataDF[file].to_csv('Annual_Metrics.csv', mode='a')
        # add a column for river names as Station and output annual to .txt
        AA_df = pd.DataFrame(AnnualAverages[file])
        Station = pd.DataFrame(file,index=['Station'],columns=[0])
        AA_Df = Station.append(AA_df)
        AA_Df.to_csv('Average_Annual_Metrics.txt', sep='\t', mode='a', header=False)
        
        # add a column for river names as Station and output monthly to .csv
        MoDataDF[file].insert(0,'Station',file)
        MoDataDF[file].to_csv('Monthly_Metrics.csv', mode='a')
        # add a column for river names as Station and output monthly to .txt
        MonthlyAverages[file].insert(0,'Station',file)
        MonthlyAverages[file].to_csv('Average_Monthly_Metrics.txt', sep='\t', mode='a', header=True)