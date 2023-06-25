#set of utility functions and variables
#for the encounter_calibration code

import numpy as np

CR_to_XP={'0':10,
          '1/8':25,
          '1/4':50,
          '1/2':100,
          '1':200,
          '2':450,
          '3':700}

#for now, we only have values for 1st level
XP_difficulty_by_level={1:\
                    {'easy':,
                    'medium':,
                    'hard':,
                    'deadly':}
                    }

def calculate_difficulty(CRs,num_pcs=5,levels=1,return_type=True):
    #force this for now
    levels=1
    
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
    
    if return_Type:
        difficulty_boundaries=calculate_difficulty_boundaries(num_pcs,levels)
        
        #need to decide if I want to introduce some sort of
        #"trivial" category if we're below the easy boundary
        
        difficulty_index=max(difficulty_boundaries[:,1]\
                                .searchsorted(XP_total)-1,0)
        
        return XP_total,difficulty_boundaries[diffculty_index,0]
    
    else:
        return XP_total

def calculate_difficulty_boundaries(num_pcs=5,levels=1):
    #force this for now
    levels=1
    
    boundaries=np.empty((4,2),dtype=object)
    
    for idx,cat in ['easy','medium','hard','deadly']:
        boundaries[idx][0]=cat
        #if levels is an iterable, num_pcs is ignored
        if hasattr(levels,'__iter__'):
            boundaries[idx][1]=sum([XP_difficulty_by_level[lvl][cat] \
                                for lvl in levels])]])
        
        else:
            boundaries[idx][1]=XP_difficulty_by_level[levels][cat]*num_pcs
    
    return boundaries
    
    
    
    