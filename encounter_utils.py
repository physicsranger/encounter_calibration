#set of utility functions and variables
#for the encounter_calibration code

import numpy as np
import time
from functools import reduce

CR_to_XP={'0':10,
          '1/8':25,
          '1/4':50,
          '1/2':100,
          '1':200,
          '2':450,
          '3':700}

#for now, we only have values for 1st level
XP_difficulty_by_level={1:\
                    {'easy':25,
                    'medium':50,
                    'hard':75,
                    'deadly':100}
                    }

CR_ave_HP={'0':3.5,
	               '1/8':21,
	               '1/4':42.5,
	               '1/2':60,
	               '1':78,
	               '2':93,
	               '3':108}

def CR_to_float(CR):
    return reduce(lambda n,d:float(n)/float(d),CR.split('/')) \
      if len(CR)>1 else float(CR)

#will likely want to think of how to check/enforce
#that CRs should be string or iterable of strings
def calculate_difficulty(CRs,num_pcs=5,levels=1,return_category=True):
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
    
    else:
        return XP_total

def calculate_difficulty_boundaries(num_pcs=5,levels=1):
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
    
def add_enemies(possible_CRs,enemy_group,rng=None,SEED=None):
    #create an empty list to fill
	enemies=[]
	
	#check on the random number generator
	if rng is None:
	    rng=np.random.default_rng(seed=int(time.time()) if SEED is None else SEED)
	
	#set a maximum number of enemies to control the while loop
	#if num_members is 0, then set an unrealistically high number
	num_max=enemy_group.num_members if enemy_group.num_members>0 else 100
	    
	#now we want a limiting value based on the requested difficulty
	if enemy_group.difficulty is not None:
	    boundaries=calculate_difficulty_boundaries(enemy_group.num_pcs,
	                                                enemy_group.pc_levels)
	        
	    #quickly turn it into a dictionary for ease
	    idx=1 if enemy_group.difficulty=='easy' else \
	        2 if enemy_group.difficulty=='medium' else \
	        3
	        
	    XP_limit=boundaries[idx][1]
	        
	    #for a deadly encounter, this is somewhat open ended
	    #but let's make sure that it isn't more than twice the limit
	    #in case number of enemies was not specified
	    if enemy_group.difficulty=='deadly':
	        XP_limit*=2
	
    #continue adding as long as we haven't eliminated all
	#possible CR values or met the requested number of enemies
	while possible_CRs and len(enemies)<num_max:
	    #randomly select a challenge rating for a possible new enemy
	    new_enemy=rng.choice(possible_CRs,1)[0]
	        
	    #if we have a target difficulty
	    if enemy_group.difficulty is not None:
    	    #check if that pushes us past the XP_limit
	        this_XP=calculate_difficulty(enemies+[new_enemy],
	                                     enemy_group.num_pcs,
	                                     enemy_group.pc_levels,
	                                     return_category=False)
	        
    	    #if we're under the limit, add the enemy
	        if this_XP<XP_limit:
	            enemies.append(new_enemy)
	         
	        #otherwise, remove the new_enemy challenge rating from
	        #our choices as it will increase the value too much
	        else:
	            possible_CRs.remove(new_enemy)
	        
	    else:
	        enemies.append(new_enemy)
	
	return enemies
    
    