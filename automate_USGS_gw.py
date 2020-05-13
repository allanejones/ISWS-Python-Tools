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

def convert_LatLong_to_Lambert( lat, long, reverse=False ):
    """
    Converts a pandas.Series of latitude and longitude data into LambertConical
    data (in feet) which are returned as pandas.Series to user.

    Parameters
    ----------
    lat  : pandas.Series
        Latitude data input as a pandas.Series. Assumed coordinate reference
        system (CRS) is 'WGS84'.
    long : pandas.Series
        Longitude data input as a pandas.Series. Assumed coordinate reference
        system (CRS) is 'WGS84'.

    Returns
    -------
    Lam_x_ft : pandas.Series
        Converted longitude data in Lambert CRS with units of feet.
    Lam_y_ft : pandas.Series
        Converted latitude data in Lambert CRS with units of feet.

    """
    
    #imports 
    import cartopy.crs as ccrs
    import pandas as pd
    # conversion
    ft2m = 0.304800609601219
    m2ft = 1/ft2m
    # finalizing the ISWS Lambert projection
    false_east = 2999994.0 * ft2m # feet to meters?
    false_north = -50.0 * ft2m # meters -> fudge factor to realign shapefile with basemap.
    illimap = ccrs.LambertConformal( false_easting=false_east,
                                     false_northing=false_north,
                                     central_longitude=-89.50,
                                     central_latitude=33.00,
                                     standard_parallels=(33,45) )
    # define USGS coordinate system
    USGS_crs = ccrs.Geodetic()
    # determine which crs should be first <-- !!! NEW !!!
    if reverse:
        desired_crs = USGS_crs
        src_crs = illimap
    else:
        desired_crs = illimap
        src_crs = USGS_crs
    # transform points from within dataframe
    Lam_x_m = pd.Series(1e-36, index=long.index ) # storage variable
    Lam_y_m = pd.Series(1e-36, index=lat.index )  # storage variable
    for idx in long.index:
        Lam_x_m.loc[idx], Lam_y_m.loc[idx] = \
            desired_crs.transform_point( long.loc[idx], 
                                         lat.loc[idx], 
                                         src_crs)
    # convert to ft
    Lam_x_ft = Lam_x_m*m2ft
    Lam_y_ft = Lam_y_m*m2ft
    # return the DataFrame
    return Lam_x_ft, Lam_y_ft



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
               'DTW_Value': [],
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
                outdict['DTW_Value'].append( float(parsed['value'][iii]) )
                outdict['SiteName'].append( csvdict[site][0] )
                outdict['SiteLongitude'].append( float(csvdict[site][3]) )
                outdict['SiteLatitude'].append( float(csvdict[site][4]) )
    # convert the spatial points from LatLong to Lambert
    outdf = pd.DataFrame(outdict)
    outdf['Lam_x_ft'], outdf['Lam_y_ft'] = convert_LatLong_to_Lambert(
            outdf['SiteLatitude'], outdf['SiteLongitude'] )
    # return the final data
    return outdf
                
        
    
#%% PLOTTING FUNCTIONS

def plot_pertinent_USGS_1to1( ax, mf, df, hds, yr, kper=0 ):
    """
    Plots the pertinent USGS data for a 1:1 plot comparing observed and modeled
    head data for the ESL area.

    Parameters
    ----------
    ax : matplotlib axes
        The axws where USGS data is to be plotted
    mf : flopy.modflow.mf.Modflow object
        Flopy.modflow object that contains a "complete" (i.e., fully 
        initialized) model.
    df : pandas.DataFrame
        A pandas DataFrame that contains the downloaded USGS hand measurement 
        data downloaded from online.
    hds : numpy.ndarray of modeled heads from completed model run
        This array provided the head data from a completed model run. The shape
        of this array is (npers, nlays, nrows, ncols).
    yr : int, float, string 
        The desired year of plotting data, from 01 Jan. 'yr' to 31 Dec. 'yr'+1.
    kper : int
        The desired stress period to plot. 

    Returns
    -------
    None. --> Plots information onto a provided axis.

    """
    
    # import
    import pandas as pd
    import numpy as np
    import flopy
    # obtain pertinent data
    yr = int(yr)
    idx = ( (df['DateTime'] >= pd.to_datetime(yr,   format='%Y')) & 
            (df['DateTime'] <  pd.to_datetime(yr+1, format='%Y')) )
    # if no data found, break method
    if not idx.any():
        print('ISWS Update: USGS data not found for year of {}.'.format(yr))
        return
    # if data found, continue on...
    pertdata = df.loc[idx, :]
    # obtain model data
    d = mf.get_package( 'DIS' ) # discretization package
    e = mf.modelgrid.top_botm # model elevations
    # create storage variables
    obs_head     = -1e36*np.ones( (pertdata.shape[0],) )
    modeled_head = -1e36*np.ones( (pertdata.shape[0],) )
    # loop through and process pertinent values
    for iii, idx in enumerate(pertdata.index):
        try:
            # find rc    
            rrr, ccc = d.get_rc_from_node_coordinates( pertdata.loc[idx, 'Lam_x_ft'],
                                                       pertdata.loc[idx, 'Lam_y_ft'], 
                                                       local=False )
            # find surface elevations --> calculate USGS heads
            cur_e = e[0, rrr, ccc]
            obs_head[iii]     = cur_e-pertdata.loc[idx,'DTW_Value']
            modeled_head[iii] = hds[kper,0,rrr,ccc]
        except:
            # site not found, continue to next
            obs_head[iii]     = np.nan
            modeled_head[iii] = np.nan
    # ^^^ data found and saved in pertinent DF ^^^
    # compare against modeled heads
    ax.plot( obs_head, modeled_head, marker='^', ms=10, color='forestgreen',
             label='USGS hand measurements')
    # function complete
    return
