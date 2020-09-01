# -*- coding: utf-8 -*-
"""
This script is to generate randomized lists of coffee pairings for "Random 
Coffees" for promoting collaboration and community during COVID19 (and beyond).

Created on Fri Jul 31 10:13:21 2020

@author: alljones
"""

class RandomCoffees:
    
    # read participants from list in folder
    def __get_participants(self, fp=''):
        # imports
        import os
        # get the list of participants from text file
        with open( os.path.join(fp,'participant list.txt'), 'r') as fid: # 'WSP Central Random Coffee.txt'
            lines = fid.read().split('\n')
        # loop through lines and strip information
        self.pd={}
        for line in lines:
            name, email = line.split('\t\t')
            self.pd[name] = {'Contact': email, 
                             'Previous Pairs': [],
                             'Dates': []}
        # get list of names from participant dictionary
        self.names = list( self.pd.keys() )
        # add a 'None' value, if an odd number of participants
        if len(self.names) % 2 != 0:
            self.names.append(None)
            self.pd[None] = {'Contact':None,
                             'Previous Pairs': [],
                             'Dates':[] }
    
    def __check_if_valid(self, rrr):
        for i in range(rrr.shape[0]):
            # grab names
            nm1 = self.names[rrr[i,0]]
            nm2 = self.names[rrr[i,1]]
            if nm2 in self.pd[nm1]['Previous Pairs']:
                return False
        # if you have made it this far, array is unique
        return True
        
    def __create_pairings(self):
        # imports
        import numpy as np
        # unique array found?
        found=False
        # grab random array
        rrr = np.arange( int(len(self.names)) )
        while not found:
            # suffle the array
            np.random.shuffle( rrr )
            if self.__check_if_valid( rrr.reshape(int(len(self.names)/2),2) ):
                found=True
                rrr = rrr.reshape(int(len(self.names)/2),2)
        # unique pairing found!
        cpairs = []
        for i in range( rrr.shape[0] ):
            # getting names
            nm1=self.names[rrr[i,0]]
            nm2=self.names[rrr[i,1]]
            # recording names
            self.pd[nm1]['Previous Pairs'].append( nm2 )
            self.pd[nm2]['Previous Pairs'].append( nm1 )
            self.pd[nm1]['Dates'].append( self.ncd )
            self.pd[nm2]['Dates'].append( self.ncd )
            # record pairing
            cpairs.append( (nm1, nm2) )
        # store the final pairings
        self.date_sched[self.ncd]=cpairs
        
    # determine whether to reset the list of Previous pairings    
    def __reset_previousPairs(self):
        for key in self.pd.keys():
            if len(self.pd[key]['Previous Pairs']) == len(self.names)-1:
                self.pd[key]['Previous Pairs'] = []
                
    def write_schedule( self, fp='' ):
        # imports
        import os
        # get the list of participants from text file
        fn = self.first_date.strftime('%Y%m%d')+'_schedule.txt'
        with open( os.path.join(fp, fn), 'w') as fid:
            for date in self.date_sched.keys():
                # write the date
                fid.write( 'Week of '+date.strftime('%d-%b-%Y')+'\n')
                # Write the pairings and their contact info
                for entry in self.date_sched[date]:
                    # create output string 1
                    if entry[0] is not None:
                        out1 = '{} {}'.format( entry[0], 
                                               self.pd[entry[0]]['Contact'] )
                    else:
                        out1 = '***'
                    # create output string 2
                    if entry[1] is not None:
                        out2 = '{} {}'.format( entry[1], 
                                               self.pd[entry[1]]['Contact'] )
                    else:
                        out2 = '***'
                    # write the pairings in the file
                    fid.write( '{} -- {}\n'.format(out1, out2) )
                # finished with pairings, write spaces before next date    
                fid.write('\n\n\n')
            # finished writing schedule
            

#%% INITIATE THE READING OF THE .LST FILE
    def __init__(self):
        # imports
        import pandas as pd
        # obtain the next coffee date
        next_coffee = input('Please input the next coffee date ("yyyy-mm-dd"): ')
        self.ncd = pd.to_datetime(next_coffee)
        self.first_date = pd.to_datetime(next_coffee)
        # update user
        print('Thank you.')
        # obtain the number of weeks we are planning for
        self.nwks = int(input('How many weeks are we planning? Input: '))
        # update user
        print('Thank you.')
        
        # obtain participants information
        self.__get_participants()
        
        # create pairings
        self.date_sched = {}
        for n in range( self.nwks ):
            # update user
            print( "Week {} of {}.". format(n+1, self.nwks))
            # create pairings
            self.__create_pairings()
            # update date
            self.ncd += pd.DateOffset(7)
            # check if need to reset previous pairings...
            self.__reset_previousPairs()
            
        # write pairings to text file:
        self.write_schedule()
        
        # update user
        print('Scheduling complete.')
        
        
        
#%% TESTING THE CLASS
# run script to test    
if __name__ == "__main__":
    # test the class
    test = RandomCoffees()

