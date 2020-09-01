"""
A module that helps deal with administrative/logistical issues concerning
computer/file organization.

Author: Allan E. Jones
Date: 25 Nov. 2019

'Good luck, brave Sir Lancelot. God be with you.'-King Arthur
"""

#%% GLOBAL IMPORTS
import os

#%% CREATE FOLDERS

#!!! THIS IS LIKELY TAKEN CARE OF WITH BETTER USE OF OS._METHODS
# # creating a module of administrative (e.g., directory-related) issues
# def check_folders( path, make_um=True ):
#     # split path up and check if exists and create necessary paths
#     if '/' in path:
#         parts = path.split( '/' )
#     else:
#         parts = path.split('\\')

#     # recombine path by parts and create necessary folders    
#     for idx in range( len(parts) ):
#         # skip if checking that '..' exists
#         if parts[idx] != '..' or parts[idx] != '.':
#             recon_path = '/'.join( parts[:idx+1] ) # reconstruct path in parts
#             # if reconstructed path does not exist, make it!
#             if not os.path.isdir( recon_path ) and make_um:
#                 os.mkdir( recon_path )
#                 # do this for all paths.
#             elif not os.path.isdir( recon_path ) and not make_um:
#                 print('\n***'+
#                       '\nThe following parent folders does not exist.\n'+
#                       recon_path+
#                       '\n***\n')
#                 break
#             elif os.path.isdir( recon_path ) and idx == len(parts)-1:
#                 print('\n***'+
#                       '\nThe input path exists.\n'+
#                       recon_path+
#                       '\n***\n')
#                 break
# #=============================
    

def MakeEntirePath( p ):
    """
    Checks for existence of desired path/directory and creates all necessary
    segments of that path.

    Parameters
    ----------
    p : string
        Desired save path.

    Returns
    -------
    None.

    """
    # imports 
    import os
    # properly split path into parts
    if '/' in p and '\\' in p:
        p = p.split('/')
        for n, i in enumerate( p ):
            if '\\' in i:
                p.remove(i)
                for m, j in enumerate(i.split('\\')):
                    p.insert(n+m, j)
    elif '/' in p:
        p = p.split('/')
    elif '\\' in p:
        p = p.split('\\')
    # combine, check, and make paths one at a time
    a = ''
    for i in p:
        a = os.path.join(a,i)
        if not os.path.exists(a):
            os.mkdir(a)
    # return the useful data
    return



#%% MODULE RUN AS SCRIPT    

# creating the module names
if __name__ == "__main__":
    
    # run the hello world script
    inns = input( 'Enter a path below:\n'+
                  '(Do not include any syntactical marks.)\n' )
    check_folders( inns, make_um=False )
    
    # update user that run is finished
    print('Completed module run "as script".')

    