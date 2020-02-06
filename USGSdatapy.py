# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:57:40 2020

@author: alljones
"""

#%% IMPORTS
import os
import pandas as pd
import numpy as np

#%% universal functions??

# public - method to read data from tab-separated USGS file
def read_tab_separated_USGS(filename=None, filepath=None):
    #!!! Expansion: allow user to specify a file to read here...
    if filename is None:
        raise Exception('AEJ: No filename provided.')
    # assumes current working directory if no filepath specified
    if filepath is None:
        filepath = os.getcwd()
    # ensure file path ends in a '/' or '\\'
    if filepath[-1] != '/' or filepath[-1] != '\\':
        filepath += '/'
    #create a dictionary for storage, eventual conversion to pd.df
    data = {}
    usgsdoc = []
    
    # open text file and read in the data
    with open(filepath+filename, 'r+') as fid:
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
    replace= __parse_USGS_parameters( usgsdoc )
    
    # pop the old keys out, and replace with new keys
    for ok in replace:
        data[ replace[ok] ] = data.pop( ok )
        
    # return the DataFrame returned by dictionary
    return pd.DataFrame( data )
  

      
# **private** - method helps swap out columns of interest
def __parse_USGS_parameters( doclist ):
    # review usgs documentation info and determine valuable column header info
    parameter_description=[]
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
            parameter_description.append( line )
            
    # create dictionary of key_id and replacement value
    ddd={}
    for line in parameter_description[2:]: 
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




#%% USGS CLASS

# create a USGS data class...?
class USGSdata:
    
# **private** - method writes data to .json file if read in from .txt file -> save time in long run?
    #!!! EXPANSION: save to "universal" water file format type
    def __write_to_json(self):
        # Prompt for file name
        savefile=input('Attempting to write Pandas DataFrame to .JSON file for:\n'+
                       '{}\n\n'.format( self.__fn.split('/')[-1] )+
                       'Would you like to set the filename?\n'+
                       '1. "" (Press Enter) -> enter nothing to reuse same filename/path\n'+
                       '2. "no" -> enter "no" to abort file save\n'+
                       '3. "[Insert file name]" -> enter desired filename/path\n'+
                       'Type here: ')
        print() # add a spacer line...
        # respond to prompt
        if savefile.lower() == 'no':
            return # exit the function without doing anything
        elif len( savefile ) == 0:
            # use the same file name
            savefile = self.__fn
            savefile = savefile.split('.')[:-1]
            savefile.append( 'json' )
            savefile = '.'.join( savefile )
        #ELSE: savefile stays as input
        
        # check for valid file name    
        if savefile[-5:] != '.json':
            raise Exception('AEJ: Filename ("{}") is not prepared properly.'.format(savefile)+
                            ' It requires ".json" suffix.')   
        
        # using the prepared filename, save the DataFrame to the file
        with open( savefile, 'w') as fileout:
            fileout.write( self.data.to_json(orient='table') )
        # update user
        print( 'Data written to .json file: {}'.format( savefile.split('/')[-1] ) )

# **private** - method reads data from .json file
    def __get_data_from_json(self):
        self.data = pd.read_json( self.__fn, orient='table', typ='frame' )
        print('Data read from file: {}'.format( self.__fn.split('/')[-1]) )
    
# **private** - method reads data from .txt file during initiation of class    
    def __get_data_from_tab_separated(self):
        self.data = read_tab_separated_USGS( self.__fn.split('/')[-1], self.__fp )
        print('Data read from tab-separated file: {}'.format(self.__fn.split('/')[-1]) )
        # write to .json file
        self.__write_to_json()


#========== INITIALIZE THE CLASS
    # initialization function for class
    def __init__(self, filename=None, filepath=None ):        
        # require a filename
        if filename is None:
            raise Exception('AEJ: No filename provided.')
        else:
            # recording the filename and path
            if filepath is None:
                self.__fp = os.getcwd()
            else:
                self.__fp = filepath
                           
            # check for .json files with same root name
            possiblefiles=os.listdir( filepath )
            for fn in possiblefiles:
                if fn.split('.')[:-1] == '.'.join(filename.split('.')[:-1]) and \
                   fn.split('.')[-1] =='json':
                       filename = fn
                       break # found match no need to search further

            # recording the filename and path
            self.__fn = filepath + filename
            
            # use filename and path to read in the data
            if self.__fn.split('.')[-1] == 'json':
                self.__get_data_from_json()
            else:
                self.__get_data_from_tab_separated()
                
        #!!! Expansion: retain meta-header information somehow
 

#%% Running the file as a whole       
if __name__ == "__main__":
    
    # defining the path names
    test = USGSdata(filename='20140621-20200101_NorthBarrington.txt',
                    filepath='C:/Users/alljones/Box/BACOG_2020/USGS Data/Groundwater/')
    
    
        
        