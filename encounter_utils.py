#set of utility functions and variables
#for the encounter_calibration code

import numpy as np
import time
from functools import reduce

'''
look-up dictionary for XP by challenge rating
'''

CR_to_XP={'0':10,
          '1/8':25,
          '1/4':50,
          '1/2':100,
          '1':200,
          '2':450,
          '3':700}

'''
look=up dictionary for difficulty XP thresholds
by character level, for a single character,
currently, only have values for 1st level
'''

XP_difficulty_by_level={1:\
                    {'easy':25,
                    'medium':50,
                    'hard':75,
                    'deadly':100}
                    }

'''
look-up dictionary for the average enemy hit points
based on challenge rating
'''

CR_ave_HP={'0':3.5,
	       '1/8':21,
	       '1/4':42.5,
	       '1/2':60,
	       '1':78,
	       '2':93,
	       '3':108}

'''
look-up dictionary for the average enemy damage
per round based on challenge rating
'''

CR_ave_DMG={'0':1,
            '1/8':1.5,
            '1/4':4.5,
            '1/2':7,
            '1':11.5,
            '2':17.5,
            '3':23.5}

def CR_to_float(CR):
    '''
    function to convert challenge rating string to a
    float value for tasks such as magnitude comparison
    (e.g., '1/4' -> 0.25)
    
    Parameters
    ----------
    CR - str
        string representation of a challenge rating
    
    Returns
    -------
    float
        the float representation of the input challenge
        rating string
    '''
    
    
    return reduce(lambda n,d:float(n)/float(d),CR.split('/')) \
      if len(CR)>1 else float(CR)

def valid_difficulty(DIFFICULTY):
    '''
    function to check if a requested encounter difficulty
    string is valid
    
    Parameters
    ----------
    DIFFICULTY - str
        an encounter difficulty
    
    Returns
    -------
    bool
        if the input DIFFICULTY is valid
    '''
    
    return DIFFICULTY.lower() in ['easy','medium','hard','deadly']

#will likely want to think of how to check/enforce
#that CRs should be string or iterable of strings
def calculate_difficulty(CRs,num_pcs=5,levels=1,return_category=True):
    '''
    function to calculate the encounter difficulty given challenge rating
    information, number of PCs, and level(s) of PCs
    
    Parameters
    ----------
    CRs - list
        the challenge ratings of enemies in the encounter
    num_pcs - int
        the number of PCs for which the encounter difficulty should
        be calibrated
    levels - int or list
        level(s) of PCs for which the encounter difficulty should
        be calibrated, currently this is forced to be 1 but future
        updates may allow for higher levels and a mix of values
    return_category - bool
        flag to return the categorical, string representation of
        the calculated encounter difficulty
    
    Returns
    -------
    float
        total XP of the encounter, taking into account modifiers
        based on number of enemies and number of PCs
    str
        calculated encounter difficulty category, optional 
    '''
    
    #force this for now
    levels=1
    
    #get the number of enemies and base sum of XP
    #based on the challenge ratings
    if hasattr(CRs,'__iter__'):
        num_enemies=len(CRs)
        XP_total=sum([CR_to_XP.get(cr) for cr in CRs])
        
    else:
        num_enemies=1
        XP_total=CR_to_XP.get(CRs)
    
    #modifier for total XP based on number of enemies
    encounter_mod=1 if num_enemies<2 else \
                    1.5 if num_enemies<3 else \
                    2 if num_enemies<7 else \
                    2.5 if num_enemies<11 else \
                    3 if num_enemies<15 else \
                    4
    
    #adjust the modifier based on party size
    if num_pcs<3:
        encounter_mod=encounter_mod+0.5 if encounter_mod<3 \
                      else encounter_mod+1
    
    elif num_pcs>5:
        encounter_mod=encounter_mod-0.5 if encounter_mod<4 \
                      else encounter_mod-1
    
    XP_total*=encounter_mod
    
    #if the user wants the difficulty category, get the boundaries
    #and return the corresponding string representation with
    #the total summed and adjusted XP
    if return_category:
        difficulty_boundaries=calculate_difficulty_boundaries(num_pcs,levels)
        
        #need to decide if I want to introduce some sort of
        #"trivial" category if we're below the easy boundary
        
        #get the index where XP_total would be inserted to keep order
        #and then subtract 1, add small amount to XP_total
        #to reflect the >= aspect of difficulty boundaries
        difficulty_index=max(difficulty_boundaries[:,1]\
                                .searchsorted(XP_total+0.005)-1,0)
        
        return XP_total,difficulty_boundaries[difficulty_index,0]
    
    #otherwise, just return the XP total
    else:
        return XP_total

def calculate_difficulty_boundaries(num_pcs=5,levels=1):
    '''
    function to calculate the encounter difficulty XP lower
    boundaries based on the number of PCs and PC level(s)
    
    Parameters
    ----------
    num_pcs - int
        number of PCs for calibrating the encounter difficulty
        XP boundaries
    levels - int or list
        level(s) of PCs for calibrating the encounter difficulty
        XP boundaries, currently this is forced to 1 but future
        updates may allow for higher levels and a mix of values
    
    Returns
    -------
    array
        a (4,2) array with form [difficulty category,XP_boundary]
    '''
    
    #force this for now
    levels=1
    
    boundaries=np.empty((4,2),dtype=object)
    
    for idx,cat in enumerate(['easy','medium','hard','deadly']):
        boundaries[idx][0]=cat
        
        #if levels is an iterable, num_pcs is ignored
        if hasattr(levels,'__iter__'):
            boundaries[idx][1]=sum([XP_difficulty_by_level[lvl][cat] \
                                for lvl in levels])
        
        else:
            boundaries[idx][1]=XP_difficulty_by_level[levels][cat]*num_pcs
    
    return boundaries
    
    