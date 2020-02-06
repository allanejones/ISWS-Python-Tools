"""
This module automates the process for reading/parsing the data provided 
from Groundwater Vistas HSU Summary files.

@author: alljones

"It's... "
"""


#%% GLOBAL IMPORTS
import numpy as np
import pandas as pd

# import homebrewed functions
from adminpy import check_folders

#%% INSERT FUNCTIONS TO AUTOMATE THE READING/PARSING OF HSU SUMMARY FILES

# function that reads the hsu file
def scrape_hsu_csv( filename ):
    # first read in the data file
    with open( filename, 'r' ) as fid:
        raw_csv = []
        # loop through file    
        for line in fid.readlines():
            # retain rest of the raw_csv file as lists
            raw_csv.append( line.rstrip('\n').split(',') )
            # determine which line has the timestamp data
            if 'Time Values' in line:
                # remove return character, split by comma, lose row heading
                times = line.rstrip('\n').split(',')[1:]
        
    # convert list items: str -> double/float
    times = np.asarray( [ float(stamp) for stamp in times] )
    
    # return the "raw_csv data and the timestamps
    return raw_csv, times
#===================
    


# read through list and obtain data
def csv_sections( datalist ):
    # initializing variables
    data_sections   = {}
    correct_section = False
    # create header key
    row_hdr = ( 'Summary of Flows for HSU Zone' )
    
    # search datafile to find the lines of data
    for entry in datalist:
        # checking for the key in list - start of section
        if row_hdr in entry[0]:
            correct_section = True
            # initializing the dictionary key
            cur_key = int(entry[0].split(' ')[-1])
            data_sections[ cur_key ] = []
        # checking for key not in list - end of section    
        elif entry[0] == '':
            correct_section = False
        # record the rows within the section
        elif correct_section:
            data_sections[ cur_key ].append( entry )
            
    # return the desired dictionary
    return data_sections
#===================



# convert the list data in each dict. entry into dict. with keys for "columns"
def translate_data2dictionary( datavar ):
    # the overall dictionary that will house inner dictionaries for each HSU
    # ex: outer[ HSU_# ] = inner{ col1: [data (array)], col2: ....} 
    outer = {}
    
    # loop through the passed dictionary entries
    for okey in datavar.keys():
        # establish inner dictinary to record data and columns
        inner = {}
        
        # loop through the entries in the passed dictionary entry
        # i.e., select row of HSU dataset
        for entry in datavar[ okey ]:
            # create data list
            data_array = []
            
            # loop items in row of HSU dataset/sheet, exclude header
            for item in entry[1:]:
                if item == '-1.#QNAN0e+000' or item == '1.#QNAN0e+000':
                    data_array.append( np.nan )
                else: 
                    
                    try:
                        data_array.append( float(item) )
                    except:
                        
                        raise Exception('Here is the issue: {}'.format(item))
                            
            # create array from data list
            data_array = np.asarray( data_array )
            
            # set row header as dictionary key - add in array and sum
            inner[ entry[0] ] = data_array # unneeded sum can calculate later
        
        # record inner dictionary as item in outer dictionary
        outer[ okey ] = inner
        
    # return outer dictionary when complete
    return outer
#===================
 
    

def dict2pandas( datavar, timestamps ):
    # create dataframe for each HSU
    list_df = []
    for key in datavar.keys():
        # create dataframe from data
        minidf = pd.DataFrame( datavar[key] )
        # add the model timestep information
        minidf['Time Steps'] = timestamps
        # add HSU "name" information
        outtext = ("Enter the name of HSU "+str(key)+":\n")
        namer   = input(outtext)
        if namer == '':  # i.e., No name is input
            namer = key
        # add in the HSU name information
        minidf['HSU Name'] = namer
        # add the "minidf" to the list
        list_df.append( minidf )
        
    # concatenate all dataframes
    big_df = pd.concat( list_df )
    
    # return final large datset
    return big_df    
#===================



def save2json( df, filepath ):
    # if directory, create directory
    if '\\' in filepath:
        parts = filepath.split('\\')
    elif '/' in filepath:
        parts = filepath.split('/')
    
    # compile directory without filename
    path = '/'.join( parts[:-1] )
    path += '/'
    # create directory
    check_folders( path )
    
    # write .json file
    with open( path+parts[-1], 'w') as fileout:
        fileout.write( df.to_json(orient='table') )
#===================



#%% PRIMARY FUNCTION TO RUN MODULE
# this is the function the is called and works the entire module
def read_hsu( filename, save_json='nope'):
    """
    Provide filename of HSU Summary to be read.
    
    And if you want to save a .json file of the resulting dataframe, provide 
    the filename/entire directory for saving the information.
    
    For some reason, the prescribed indices are not maintained when returning
    the dataframe. Thus, the user will need to define the desired indices after
    reading in the data.
    
    Example:
    # set indices
    final_df.set_index( ['HSU Name', 'Time Steps'] )
    
    """
    
    # scrape the original csv file for information
    rawdata, timestamps = scrape_hsu_csv( filename )
    
    # obtain data from csv list and in dictionary with HSU #s as keys
    section_dict = csv_sections( rawdata )
    
    # convert section dictionary into nested dictionary with data arrays
    datadict = translate_data2dictionary( section_dict )
    
    # convert and combine data dictionaries into one large pandas.DataFrame
    final_df = dict2pandas( datadict, timestamps )
    
    # save as a json file
    if save_json != 'nope':
        save2json( final_df, save_json )

    return final_df
    
    
    
#%% run script to test    
if __name__ == "__main__":
    
    # defining the path names
    earlypath = 'C:/Users/alljones/Documents/Water Supply Planning/Middle Illinois'
    path2data = '/2019 Recharge-MassBalance data files/HSU summaries/'
    filename  = 'test_hsu.csv'
    
    # out saving....
    jsonfile = 'test.json'
    
    # grabbing the data
    testout = read_hsu( earlypath+path2data+filename, 
                        save_json=(earlypath+path2data+jsonfile) )

    