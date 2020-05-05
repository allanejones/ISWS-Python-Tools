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

def parse_historic_USGS_tabDelimited(usgsstr):
    
    # create dictionary to return data
    outdict={'siteNum':[],
             'date': [],
             'value': []}
    # read through lines of 'usgsstr'
    for line in usgsstr.split( '\\n' ):
        if line.startswith( 'USGS' ):
            dat = line.split('\\t')
            # append the appropriate data
            outdict['siteNum'].append( dat[1] )
            outdict['date'].append( dat[3] )
            outdict['value'].append( dat[6] )
    # after completing loop, return dictionary
    return outdict


def obtain_historic_USGS_gw(fn, param='72019' ): # url='default',
    
     # param = Depth to Water from surface elevation
    # imports <-- may be unnecessary
    import urllib, json
    import pandas as pd
    
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
    
    # == OBTAIN DATA FROM ONLINE == 
    # create output dictionary --> convert to pd.DataFrame when return
    outdict = {'SiteNum': [],
               'DateTime': [],
               'Value': [],
               'SiteName': [],
               'SiteLongitude': [],
               'SiteLatitude': []
               }
    # creatE the final URL from all the sites provided
    for site in csvdict.keys():
        if site.isdigit():
            url  = ( 'https://nwis.waterdata.usgs.gov/nwis/gwlevels?'+
                     '&format=rdb'+
                     '&site_no={}'.format(site)+
                     '&parameterCd={}'.format(param) )
            # grab information from the URL
            response = urllib.request.urlopen( url )
            parsed   = parse_historic_USGS_tabDelimited( str(response.read()) )
            # loop through parsed data and store in output dictionary
            for iii in range( len(parsed['siteNum']) ):
                # append the proper data
                outdict['SiteNum'].append( site )
                outdict['DateTime'].append( pd.to_datetime( parsed['date'][iii], 
                                                            format='%Y-%m-%d' ) )
                outdict['Value'].append( float(parsed['value'][iii]) )
                outdict['SiteName'].append( csvdict[site][0] )
                outdict['SiteLongitude'].append( float(csvdict[site][3]) )
                outdict['SiteLatitude'].append( float(csvdict[site][4]) )
    # return the final data
    return pd.DataFrame( outdict )
                
        
    






#%% test the function
#imports
import os
# identify USGS .csv file
path  = '../../USGS GW dnlds'
filen = 'NWISMapperExport.csv'
# test the function
test = obtain_historic_USGS_gw( os.path.join(path, filen) )
