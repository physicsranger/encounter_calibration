#this module will define a base BattleGroup class
#as well as derived classes for the Party and the Enemies

import numpy as np
from encounter_utils import (
                     CR_to_XP,
                     XP_difficulty_by_level,
                     calculate_difficulty
                     )

class BattleGroup():
    '''
    doc string goes here
    '''
    def __init__(self,NUMBER,ATK=None,AC=None,HP=None):
        self.num_members=NUMBER
        
        #should do a check on the lengths
        if hasattr(ATK,'__iter__'):
            self.to_hit=np.round(sum(ATK)/len(ATK))
        else:
            self.to_hit=ATK
        
        if hasattr(AC,'__iter__'):
            self.armor_class=np.round(sum(AC)/len(AC))
        else:
            self.armor_class=AC
        
        if hasattr(HP,'__iter__'):
            self.hit_points=round(sum(HP))
        else:
            self.hit_points=round(NUMBER*HP)

class Party(BattleGroup):
    def __init__(self,LVL=1,EXTRAS=4,NUMBER=5,ATK=5,AC=13,HP=25/3):
        #force LVL to be 1, but we can remove
        #this later if we add capability
        LVL=1
        super().__init__(NUMBER,ATK,AC,HP)
        
        self.pc_level=LVL
        self.extras=EXTRAS
        
        #set max values now so we don't forget
        #and can compare after a 'battle'
        self.__max_extras=EXTRAS
        self.__max_hit_points=self.hit_points

class Enemies(BattleGroup):
    def__init__(self,DIFFICULTY,NUMBER=0,ATK=3,AC=13,HP=0,CRs=None,
      NUM_PCs=5,LVL_PCs=1):
        #force this for now
        LVL_PCs=1
        if not  self.valid_difficulty(DIFFICULTY):
            raise ValueError(f'Invalid encounter difficulty {DIFFICULTY}')
        
        super().__init__()
        
        self.difficulty=DIFFICULTY.lower(NUMBER,ATK,AC,HP)
        self.challenge_ratings=CRs
        self.num_pcs=NUM_PCs
        self.pc_levels=LVL_PCs
        
        if CRs is None:
            #need to build the monsters randomly
            #with logic based on if number is > 0 or = 0
            
        
        else:
            #do a check on the length of the list
            #and on if the CR level matches the difficulty category
            if hasattr(CRs,'__iter__'):
                if NUMBER>0 and len(CRs)!=NUMBER:
                    #raise some error
                
                else:
                    #the CRs variable should tell us
                    #the number of enemies, 
                    self.num_members=(self.num_members \
                      if self.num_members>0 else len(CRs))
                    
                    #now check that the calculated XP total
                    #matches the difficulty category
            
            #assume this means we want one CR for all enemies
            else:
                #do stuff
        	

    def valid_difficulty(self,DIFFICULTY):
        return DIFFICULTY.lower() in ['easy',
		    'medium','hard','deadly']
	
	def total_exp(self):
	    