# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 13:41:23 2019

@author: alljones
"""

# This is a script that tests the test function.

# add the proper directory to the sys.path variable
#import sys
#print( sys.path )
#sys.path.append( ('C:/Users/alljones/AppData/Local/'+
#                  'Continuum/anaconda3/_AEJ Function Library/') )


# check the 'PYTHONPATH' environmental variable
#import os
#print( os.environ['PYTHONPATH'].split(os.pathsep) )

#%%
# testing the newly created module
import AEJ_homebrew_LIB as hbl
hbl.hellos( 3 )

# further testing of admin functions
hbl.admin.check_folders( '../Test Folder/AEJ/' )
