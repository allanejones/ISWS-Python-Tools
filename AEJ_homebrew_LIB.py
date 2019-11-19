#%% GLOBAL IMPORTS
import os

#%% INSERT HOMEBREW FUNCTIONS OF INTEREST HERE

# defining a class of administrative (e.g., directory-related) issues
class admin:
    """
    A class that helps deal with administrative/logistical issues concerning
    computer/file organization.
    
    'Good luck, brave Sir Lancelot. God be with you.'-King Arthur
    """



    
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
#=============================
    
    



#%% MODULE RUN AS SCRIPT    

# create a test function in the hopes of eventually creating a module
def hellos( num ):
    out = 'Hello World.\n'* int(num)
    print( out )

# creating the module names
if __name__ == "__main__":
    # if run as script, update user
    print('You have run the "Homebrew Module."\n'+
          'Generally this file should not be run as a script.\n')
    
    # run the hello world script
    inns = input( 'Input an integer below:\n' )
    hellos( int(inns) )
    
    # update user that run is finished
    print('Module run "as script" complete.')

    