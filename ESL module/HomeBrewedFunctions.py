# -*- coding: utf-8 -*-
"""

This script has all of the "bespoke" functions created for the Venice and 
East St. Louis Animated Flood Risk Map scripts.

Created on Tue Nov 19 14:35:54 2019

@author: Illinois State Water Survey
"""

#%% IMPORTS

# importing functions
import os
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.special as sps
import warnings
warnings.filterwarnings("ignore")

# for testing Theis solution within polygon
import shapely

# importing a bunch of gis-related environments just for visibility of options
import matplotlib.patches as mpatches

# for gifs
import imageio

# for plotting
import cartopy.crs as ccrs

#%% BEHOLD: THE CONVERSION FACTORS
ft2m = 0.304800609601219
m2ft = 1/ft2m
g2ft3 = 7.48051948


#%% HOMEBREWED FUNCTIONS ======================================================
#==============================================================================
#==============================================================================
#%% CREATE FUNCTION TO DETERMINE POINTS WITHIN PROVIDED POLYGON

def find_cells_within_polygon( polygon, gridx, gridy ):
    # create a boolean array of 'False' values (i.e., 0)
    pts_in = np.zeros( gridx.shape, dtype='bool')

    # get bounds of polygon <- [west, south, east, North]
    bbox = polygon.bounds
    bbox_idx = np.where( (gridx >= bbox[0]) & (gridx <= bbox[2]) & \
                         (gridy >= bbox[1]) & (gridy <= bbox[3]) )

    for rowi, coli in zip( bbox_idx[0], bbox_idx[1] ):
        # check if polygon contains point -> boolean
        bool_val = polygon.contains(
                shapely.geometry.Point(gridx[rowi,coli],
                                       gridy[rowi,coli]) )
        if bool_val: # if true:
            # store True value
            pts_in[rowi, coli] = bool_val

    # ensuring points are found.
    if np.any( pts_in ):
        return pts_in
    else:
        raise Exception('Function did not find any cells within polygon.')



#%% FUNCTIONS TO DETERMINE THRESHOLD EXCEEDENCE

# function to determine the pertinent infrastructure depth for the given polygon
def determine_infrastructure_depth( grd_elev, polygon_name='undefined' ):
    # obtain proper value for polygon
    if polygon_name == 'undefined':
        raise Exception("A polygon name ('UniqueName') was not provided "+
                        "when determining the infrastructure depth.")

    # check the Missouri Avenue pipeline connection near the Ranney Well
    elif polygon_name == 'Missouri Avenue Infrastructure - Ranney':
        # determine intfrastructure depth
        out_var = np.min( grd_elev ) - 384.50  # feet - from pipeline plans
    
    # check the Missouri Avenue pipeline running North from dewatering site
    elif polygon_name == 'Missouri Avenue Infrastructure - Pipeline North':
        # determine an "avg" depth from mildly sloping pipeline
        new_avg_depth = 384.50 + ( 0.005*150.0 ) # from pipeline plans
        # determine intfrastructure depth
        out_var = np.min( grd_elev ) - new_avg_depth # feet - from pipeline plans
        
    # polygon name provided, but not correct.
    else:
        raise Exception( "Polygon {} does not exist.".format(polygon_name) )
        
    # return the determined depth, so long as it is not negative.    
    if out_var < 0:
        raise Exception( ("The depth to infrastructure"+
                          " ({:2f} ft) is invalid.").format(out_var) )
    else:
        return out_var
#===============================



# check if identified cells in solution are above ground surface
def riskType_threshold( polygon, poly_idx, water_table, grd_surface, 
                        percent_threshold=25, area='Venice', esl_sites=[]):
    
    #checking for the Venice roadway and updating the threshold
    if area=='Venice':
        if polygon.loc['RiskType'] == 3:
            # update percentile
            percent_threshold = 5
    
    # checking the ESL area sites
    else: 
        if polygon.loc['UniqueName'] in esl_sites:
            percent_threshold = 2.5
        
    # determine pertinent ground surface elevation
    grd_elev = np.percentile( grd_surface[poly_idx], percent_threshold )

    # if land use is 'road' or 'open' or 'other',
    # compare Water Table (WT) to Ground Surface (GS)
    if polygon.loc['RiskType'] in [0,3,4]:

        # risk of flooding
        if np.percentile( water_table[poly_idx],
                          percent_threshold ) >= grd_elev:
            # update the color if there are issues
            polygon.loc['PlotColors'] = 0

    # if land use is 'residential', compare WT to GS-basement depth
    elif polygon.loc['RiskType'] == 1:

        # calculate assumed basement depth
        basement_depth = np.percentile( grd_surface[poly_idx],
                                        percent_threshold ) - 5 #feet
        # risk of flooding
        if np.percentile( water_table[poly_idx],
                          percent_threshold ) >= grd_elev:
            # update the color if there are issues
            polygon.loc['PlotColors'] = 0
        # check for risk of basement flooding
        elif np.percentile( water_table[poly_idx],
                          percent_threshold ) >= basement_depth:
            # update the color if there are issues
            polygon.loc['PlotColors'] = 1

    # if land use is 'infrastructure', compare WT to infrastructure depth
    elif polygon.loc['RiskType'] == 2:

        # determine pertinent infrastructure depth
        # ^^ may need additional function to determine/pull from another area
        if 'UniqueName' in polygon.index: 
            dti = determine_infrastructure_depth( grd_surface[poly_idx],
                                                  polygon_name=polygon.loc['UniqueName'] )
        else:
            dti = 0 # fail safe in case this area is compromised accidentally?

        # calculate the infrastructure elevation - (dti) depth to infrastructure
        infra_depth = np.percentile( grd_surface[poly_idx],
                                     percent_threshold ) - dti #feet
                                    
        # risk of flooding
        if np.percentile( water_table[poly_idx],
                          percent_threshold ) >= grd_elev:
            # update the color if there are issues
            polygon.loc['PlotColors'] = 0
        # check for risk of flooding/floating important objects
        elif np.percentile( water_table[poly_idx],
                          percent_threshold ) >= infra_depth:
            # update the color if there are issues
            polygon.loc['PlotColors'] = 2

    # if land use is something else, return error.
    else:
        raise Exception( ('Error: "RiskType" {} is not currently'+
                          ' incorporated into analysis.').format(
                                 polygon.loc['RiskType']) )

    return polygon



#%% FUNCTION TO WRITE THE GIF 

# function may not be called as a part of the main regional scripts
def write_gif( pngpath, outpath='', filename='test.gif', frames_per_sec=1 ):
    # if no path designated, write the new gif to location of png files 
    if outpath == '':
        outpath = pngpath
        
    # designate the folders to search
    gif_path        = (outpath + filename)
    # find the files to write
    gif_files = [file for file in os.listdir(outpath) if '.png' in file]
    #loop through files to write to gif -> mode='I" - for multiple images
    with imageio.get_writer( gif_path,  mode='I', fps=frames_per_sec) as jiffy:
        for image in gif_files:
            jiffy.append_data( imageio.imread(outpath+image) )

    # may want to eventually use the following command to shrink gif file size
    # from pygifsicle import optimize
    # optimize( gif_path )

    # update user
    print('Gif written to following location:\n{}\n\n'.format(
            outpath + filename) )





#%% CHECK THAT THE DESIRED FOLDERS HAVE BEEN CREATED
def check_folders( path, make_um=True ):
    # split path up and check if exists and create necessary paths
    if '/' in path:
        parts = path.split( '/' )
    else:
        parts = path.split('\\')
    if make_um:
        # recombine path by parts and create necessary folders
        for idx in range( len(parts) ):
            # skip if checking that '..' exists
            if parts[idx] != '..' or parts[idx] != '.':
                recon_path = '/'.join( parts[:idx+1] ) # reconstruct path in parts
                # if reconstructed path does not exist, make it!
                if not os.path.isdir( recon_path ):
                    os.mkdir( recon_path )
                    # do this for all paths.



#%% FUNCTION TO PLOT THE RESULTS
# create function to update the plot within GIF
def plot_current_conditions( soln_dict, grd_surf_elev_array, grid_x, grid_y,
                             polygon_df, flood_indices, infra_indices,
                             bsmnt_indices, point_df, cur_time, tile_labels,
                             img_bmp, desired_fig_w=20, figsave_file='no', 
                             zoom=15 ):

#====== convert ft to meters =====
    # determine extent of plotting
    meters_extent = np.asarray([ grid_x.min(), grid_x.max(),
                                 grid_y.min(), grid_y.max() ])

    # finalizing the ISWS Lambert projection
    false_east = 2999994.0 * ft2m # feet to meters?
    false_north = -50.0 * ft2m # meters -> fudge factor to realign shapefil with basemap.
    isws_crs = ccrs.LambertConformal( false_easting=false_east,
                                        false_northing=false_north,
                                        central_longitude=-89.50,
                                        central_latitude=33.00,
                                        standard_parallels=(33,45) )
#====== convert ft to meters =====

    # determining raster scale
    height = soln_dict['bounds'][3] - soln_dict['bounds'][1]
    width  = soln_dict['bounds'][2] - soln_dict['bounds'][0]

    # Testing that the data and polygons plot atop one another
    fig = plt.figure( figsize=( desired_fig_w,
                                desired_fig_w*(height/width)) )
    fig.set_tight_layout(True)
    # Create a GeoAxes in the tile's projection
    ax = fig.add_subplot( 1,1,1, projection=isws_crs )
    # add title
    ax.set_title( "Time: {:.2f} Hour(s) ".format(cur_time), fontsize=48  )
    #setting the extent of the axis.
    ax.set_extent( meters_extent, crs=isws_crs)
    # adding the "google" basemap
    ax.imshow( img_bmp, origin='upper', 
               extent=meters_extent, transform=isws_crs )
    ax.add_image( tile_labels,  zoom, interpolation = 'spline36' )
    
    # adding the polygon patches to the map
    for idx in range( len(polygon_df) ):
        # grab the current polygon information
        poly2plot = np.asarray( polygon_df.loc[idx,'geometry'].exterior.xy ).T
        # Next, check if polygon is having issues:
        # True - color code, False - leave transparent

        # plot surface flooding
        if (flood_indices.size > 0) and (idx in flood_indices):
            ax.add_patch( mpatches.Polygon( poly2plot,
                                    edgecolor='black', linewidth=2,
                                    facecolor='black', alpha=0.55,
                                    transform=isws_crs) )

        # plot infrastructure damage
        elif (infra_indices.size > 0) and (idx in infra_indices):
            ax.add_patch( mpatches.Polygon( poly2plot,
                                    edgecolor='black', linewidth=2,
                                    facecolor='red', alpha=0.55,
                                    transform=isws_crs) )

        # plot basement flooding
        elif (bsmnt_indices.size > 0) and (idx in bsmnt_indices):
            ax.add_patch( mpatches.Polygon( poly2plot,
                                    edgecolor='black', linewidth=2,
                                    facecolor='darkorange', alpha=0.55,
                                    transform=isws_crs) )

        # plot all polygon boundaries
        ax.add_patch( mpatches.Polygon( poly2plot,
                                edgecolor='black', linewidth=2,
                                fill=False,
                                transform=isws_crs) )
# end loop through polygons ==============
        
    # adding the wells (buffer regions) to the plot
    for idx in range( len(point_df) ):
        wells2plot = np.asarray( point_df.loc[idx,'buff_geometry'].exterior.xy ).T
        ax.add_patch( mpatches.Polygon( wells2plot,
                            edgecolor='red', linewidth=2,
                            fill=False,
                            transform=isws_crs) )
# end loop through well point locations ==============

    # add legend
    legend_elements = [ mpatches.Patch( facecolor='black',
                                        edgecolor='black', #alpha = 0.55,
                                        label='Surface Flooding'),
                        mpatches.Patch( facecolor='red',
                                        edgecolor='black',
                                        label='Infrastructure Damage'),
                        mpatches.Patch( facecolor='darkorange',
                                        edgecolor='black',
                                        label='Basement Flooding') ]
#    ax.legend( handles=legend_elements,
#               title='Legend', title_fontsize=18,
#               bbox_to_anchor= (1.0015, 1, 0.15, 0.0),
#               frameon=False )
                        
    ax.legend( handles=legend_elements, loc=1,
               title='Legend', title_fontsize=21,
               fontsize=18, shadow=True )

# will add text manually in Adobe (or something)
#    # add descriptive text
#    offset = 75
#    x_text = ax.get_xlim()[-1] +offset
#    y_text = ax.get_ylim()[0] + (ax.get_ylim()[-1] - ax.get_ylim()[0])/3
#    if cur_time > 0:
#        ax.text( x_text, y_text,
#                 ('Example text:\n'+
#                  'We should\n'+
#                  'update this\n'+
#                  'to annotate\n'+
#                  'the analysis.'),
#                  fontsize=14)

    # display the image
    plt.show()

    # save figure
    if figsave_file.lower() != 'no':
        fig.savefig( figsave_file )



#%% FUNCTION TO CALCULATE THE THEIS SOLUTION FOR EACH WELL
        
def TheisFunc( x, y, Q, T, S, t_time, x_well, y_well):
    # determining radius of every grid point relative to the well
    rrr= (((x_well-x)**2)+((y_well-y)**2))**0.5
    return Q/(4*math.pi*T)*sps.exp1((rrr**2)*S/(4*T*abs(t_time)))*m2ft


#%% FUNCTION THAT HANDLES ALL OF THE THEIS SOLUTION STEPS

# convert gpm to cubic meters per hour (cmh)    
gpm2cmh = lambda aaa: aaa*60*(ft2m**3)/g2ft3

def TheisModule(aquifer, dtm_array, VeniceWells, xxx, yyy, ttt, t, 
                MAX_DD, soln_dict, counter2, welldata='nope'):
    # Loop through wells by their geometries
    # variable resets
    RunSum = np.zeros(dtm_array.shape)
    counter3 = 0
       
    # Venice calculations ==========================
    if type(welldata) == str:
        for xes, yes in zip( VeniceWells.loc[:,'geometry'].x,
                             VeniceWells.loc[:,'geometry'].y ):
            # Calculate Theis at each well and later sum (superimpose) solutions for every well for each timestep
            if ttt > 0:
                well_s = TheisFunc( xxx, yyy, aquifer['discharge'], aquifer['trans'], aquifer['stor'], ttt,
                                 xes, yes )
            else:
                # staggering the solution time for pumping and injecting by t[1]
                ttt2 = t[1] + abs(ttt)
                # continuing pumping during injecting to simulate recovery
                well_s = ( ( TheisFunc( xxx, yyy, aquifer['discharge'],
                                                 aquifer['trans'], aquifer['stor'],
                                                 ttt2, xes, yes ) ) -
                                ( TheisFunc( xxx, yyy, aquifer['discharge'],
                                                  aquifer['trans'], aquifer['stor'],
                                                  ttt, xes, yes ) ) )
            # Building MAX_DD to keep track of draw down due to each singular well (target ~ 10 ft)
            MAX_DD[counter3][counter2]= np.max(well_s)
            
            # Running sum of each well's solution (well_s) to superimpose
            RunSum = RunSum + well_s
            
            counter3 = counter3 + 1
            
            print ("Done looking at well location: ({:.2f}, {:.2f})".format(xes, yes))
    # End Venice calculations ===========================
        
    # East St. Louis Calculations =======================
    else:
        for vwi, xes, yes in zip( range( len(VeniceWells) ), 
                                  VeniceWells.loc[:,'geometry'].x,
                                  VeniceWells.loc[:,'geometry'].y ):
            # determine welldata index (wdi) from well names
            wellname = VeniceWells.loc[vwi, 'Name']
            wdi      = np.where( wellname == welldata.loc[:, 'Name'] )[0][0]
                        
            # establish variables - if well in use in Oct. 2019
            if welldata.loc[wdi, 'aej test'] == '1':
                # define well-specific discharge rate
                aquifer['discharge'] = gpm2cmh( welldata.loc[wdi, 'QQQ'] )
                
                # Calculate Theis at each well and later sum (superimpose) solutions for every well for each timestep
                if ttt > 0:
                    well_s = TheisFunc( xxx, yyy, aquifer['discharge'], 
                                                aquifer['trans'], aquifer['stor'], 
                                                ttt, xes, yes )
                else:
                    # staggering the solution time for pumping and injecting by t[1]
                    ttt2 = t[1] + abs(ttt)
                    # continuing pumping during injecting to simulate recovery
                    well_s = ( ( TheisFunc( xxx, yyy, aquifer['discharge'],
                                                     aquifer['trans'], aquifer['stor'],
                                                     ttt2, xes, yes ) ) -
                                    ( TheisFunc( xxx, yyy, aquifer['discharge'],
                                                      aquifer['trans'], aquifer['stor'],
                                                      ttt, xes, yes ) ) )
                # Building MAX_DD to keep track of draw down due to each singular well (target ~ 10 ft)
                MAX_DD[counter3][counter2]= np.max(well_s)
                # Running sum of each well's solution to superimpose
                RunSum = RunSum + well_s
                print( ("Done looking at well #{}, location: ({:.2f}, {:.2f})\n"+
                        'Discharge rate = {:.1f} gpm \n').format(vwi, xes, yes,
                                          welldata.loc[wdi, 'QQQ']) )
            # well NOT in use in Oct. 2019
            else:
                # Building MAX_DD to keep track of draw down due to each singular well (target ~ 10 ft)
                MAX_DD[counter3][counter2]= np.nan
                
            # update row counter
            counter3 = counter3 + 1
                
    # End East St. Louis calculations ==================


    # return the difference between drawdown or residual drawdown and the initial condition
    return soln_dict['init_cond'] - RunSum

#%% BEHOLD: THE CONVERSION FACTORS
ft2m = 0.304800609601219
m2ft = 1/ft2m
g2ft3 = 7.48051948