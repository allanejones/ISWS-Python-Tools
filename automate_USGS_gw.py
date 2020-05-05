# -*- coding: utf-8 -*-
"""
Use a csv from a USGS hand measurement search query to obtain the data hosted 
online. 

GOAL: 
    - input entire USGS .csv file
    - return a dataset with all the measurments and data

Created on Tue May  5 08:59:39 2020

@author: alljones
"""

def obtain_USGS_gw(fn, 
                   url=('https://nwis.waterdata.usgs.gov/nwis/gwlevels?'+
                        'site_no={}&agency_cd=USGS&format=rdb')
                   ):
    # imports <-- may be unnecessary
    import urllib, json
    
    # open the provided file and obtain data from the file
    csvdict = {}
    with open(fn, 'r') as csv:
        line = csv.readline() # first line
        while line != '':
            for iii, entry in enumerate( line[:-1].split(',') ):
                # strip off the quotation marks
                if '"' in entry:
                    entry = entry.lstrip('"').rstrip('"')
                # remove leading spaces
                if entry[0] == ' ':
                    entry = entry[1:]
                # create key for entries in dictionary
                if iii == 0:
                    key = entry
                    csvdict[key] = []
                # append to the data
                else:
                    csvdict[ key ].append( entry )
            # read next line  
            line = csv.readline()
    # finished reading USGS csv file
    
    # obtain data from online
    #   > need to record "data type"
    #       > eg- depth to water v. elevation
    url=( 'https://nwis.waterdata.usgs.gov/nwis/gwlevels?'+
          'site_no={}&agency_cd=USGS&format=json').format( list(csvdict.keys())[1] )
    response = urllib.request.urlopen(url)
    gw_data = json.loads( response.read() )
    
    
    
    # return the final data
    return gw_data # csvdict
                
        
    






#%% test the function
#imports
import os
# identify USGS .csv file
path  = '../Data Files/USGS GW dnlds'
filen = 'NWISMapperExport.csv'
# test the function
test = obtain_USGS_gw( os.path.join(path, filen) )