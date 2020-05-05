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
    """
    
    Reads the tab-delimiated USGS downlaods and returns a dicationary of the 
    siteNumber, time stamps, and measurements.

    Parameters
    ----------
    usgsstr : string
        The data from the USGS tab-delimited data sheet as a string.

    Returns
    -------
    outdict : dictionary
        A dictionary containing the data from the tab-delimited downloads.

    """
    
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


def obtain_historic_USGS_gw(fn, param='72019' ):
    """
    
    Scraps data from online USGS server (tab-delimited format) for multiple
    sites and returns a pandas.DataFrame of the data.
    
    Desired sites are read from a csv file that can be created from a USGS
    NWIS mapper query.
    
    Example:
        https://maps.waterdata.usgs.gov/mapper/nwisquery.html?URL=https://nwis.waterdata.usgs.gov/usa/nwis/gwlevels?state_cd=il&nw_longitude_va=-90.263&nw_latitude_va=38.893&se_longitude_va=-89.985&se_latitude_va=38.507&coordinate_format=decimal_degrees&format=sitefile_output&sitefile_output_format=xml&column_name=agency_cd&column_name=site_no&column_name=station_nm&date_format=YYYY-MM-DD&rdb_compression=file&list_of_search_criteria=state_cd%2Clat_long_bounding_box&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=agency_use_cd

        - Export sites from the above link as a csv.

    Parameters
    ----------
    fn : string
        A filepath including the filename.
    param : string, optional
        The USGS parameter code for the datatype to be downloaded. The 
        default is '72019', which corresponds to "depth to water from land
        surface elevation."

    Returns
    -------
    pandas.DataFrame
        A pd.DataFrame that includes the site number, time stamp, measurement
        value, site name, site longitude and site latitude for all 
        measurements.

    """
    
     # param = Depth to Water from surface elevation
    # imports <-- may be unnecessary
    import urllib
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
