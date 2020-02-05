# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:57:40 2020

@author: alljones
"""

#%% IMPORTS
import os
import pandas as pd
import numpy as np


#%% USGS CLASS

# create a USGS data class...?
class USGSdata:
    
    def read_tab_separated_USGS(self):
        #create a dictionary for storage, eventual conversion to pd.df
        data = {}
        usgsdoc = []
        
        # open text file and read in the data
        with open(self.__fn, 'r+') as fid:
            # read through the each line
            for line in fid.readlines():
                # removing the break line character ('\n') from analysis
                line = line[:-1]
                # determine variables being presented
                if '#' in line:
                    usgsdoc.append(line)                
                # grab the column headers (dictionary keys) 
                if '#' not in line and 'agency_cd' in line:
                    # create dictionary headers
                    coltitles = line.split('\t')
                    for title in coltitles:
                        data[title] = [] # create empty list to which to append data
                
                # determine if line contains data
                elif 'USGS' == line.split('\t')[0]:
                    for iii, info in enumerate(line.split('\t')):
                        # append 'nan' values if no data
                        if info == '':
                            data[ coltitles[iii] ].append(np.nan)
                        # convert to float or datetime depending upon which data is being grabbed
                        elif info[0].isnumeric() and '-' not in info:
                            data[ coltitles[iii] ].append( np.float(info) )
                        elif info[0].isnumeric() and '-' in info:
                            data[ coltitles[iii] ].append( pd.to_datetime(info, format='%Y-%m-%d %H:%M') )
                        else:
                            data[ coltitles[iii] ].append(info)
                        
        #---------- CLOSE TXT FILE
        # review usgs documentation info and determine valuable column header info
        replace=self.__parse_USGS_parameters( usgsdoc )
        
        # pop the old keys out, and replace with new keys
        for ok in replace:
            data[ replace[ok] ] = data.pop( ok )
            
        # return the DataFrame returned by dictionary
        self.data = pd.DataFrame( data )    
        
#============= PRIVATE FUNCTIONS        
    # **private** - method helps swap out columns of interest
    def __parse_USGS_parameters(self, doclist):
        # review usgs documentation info and determine valuable column header info
        self.parameter_description=[]
        rcrd=False
        for line in doclist:
            # determine correct segment of info to record
            if 'Data provided' in line:
                rcrd=True
            elif '#' == ''.join(line.split(' ')):
                # previously: '#\n' == ''.join(line.split(' ')):
                rcrd=False
            # record the proper info                
            if rcrd:
                self.parameter_description.append( line )
                
        # create dictionary of key_id and replacement value
        ddd={}
        for line in self.parameter_description[2:]: 
            # recombine string and split appropriately
            strfix = '\t'.join(line.split())
            vals   = strfix.split('\t')
            # swap --> old_key: new_key
            change=False
            for iii in range( len(vals)-2 ):
                if vals[iii][0].isnumeric() and not vals[iii+1][0].isnumeric():
                   change=iii 
            if type(change)==int:
                old_key = '_'.join( vals[1:change+1] )
                new_key = ' '.join( vals[change+1:] )
                ddd[old_key]       = old_key+'_'+new_key
                ddd[old_key+'_cd'] = old_key+'_cd'+'_'+new_key
            else:
                raise Exception('AEJ: No information was discerned from the parameter statements.')
        # return the populated dictionary
        return ddd

#========== INITIALIZE THE CLASS
    # initialization function for class
    def __init__(self, filename=None, filepath=None ):        
        # require a filename
        if filename is None:
            raise Exception('AEJ: No filename provided.')
        else:
            # recording the filename and path
            if filepath is None:
                self.__fn = os.getcwd() + filename
                self.__fp = os.getcwd()
            else:
                self.__fn = filepath + filename
                self.__fp = filepath
                
            # use filename and path to read in the data
            self.read_tab_separated_USGS()
 
       
if __name__ == "__main__":
    
    # defining the path names
    test = USGSdata(filename='20140621-20200101_NorthBarrington.txt',
                    filepath='C:/Users/alljones/Box/BACOG_2020/USGS Data/Groundwater/')
    
    
        
        