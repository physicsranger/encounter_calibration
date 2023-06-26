#this module will define a base BattleGroup class
#as well as derived classes for the Party and the Enemies

import numpy as np

import time

from encounter_utils import (
                    calculate_difficulty,
                    calculate_difficulty_boundaries,
                    CR_to_XP
                    )

class BattleGroup():
    '''
    doc string goes here
    '''
    def __init__(self,NUMBER,ATK=None,AC=None,HP=None):
        if NUMBER<0:
            raise ValueError(f'Number of members must be non-negative \
            but {NUMBER = } was passsed in')
        
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
        
        if self.armor_class<0:
            raise ValueError(f'Average armor class of battle group \
            must be non-negative, calculated AC = {self.armor_class}')
        
        if hasattr(HP,'__iter__'):
            self.hit_points=round(sum(HP))
        else:
            self.hit_points=round(NUMBER*HP)
        
        if self.hit_points<0:
            raise ValueError(f'Total hit points of battle group \
            must be non-negative, calculated HP = {self.hit_points}')

class Party(BattleGroup):
    def __init__(self,LVL=1,EXTRAS=5,NUMBER=5,ATK=5,AC=13,HP=25/3):
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
      NUM_PCs=5,LVL_PCs=1,SEED=None):
        #force this for now
        LVL_PCs=1
        
        if DIFFICULTY is None and NUMBER<=0 and CRs is None:
        
        if DIFFICULTY is not None and not self.valid_difficulty(DIFFICULTY):
            raise ValueError(f'Invalid encounter difficulty, "{DIFFICULTY}"')
        
        super().__init__(NUMBER,ATK,AC,HP)
        
        #allow that the user might not know the difficulty
        #but still want to know the expected outcome for a set number
        #of enemies of a given CR
        self.difficulty=None if DIFFICULTY is None else DIFFICULTY.lower()
        
        self.challenge_ratings=CRs
        
        #the info below is needed for the difficulty calculations
        self.num_pcs=NUM_PCs
        self.pc_levels=LVL_PCs
        
        if CRs is None:
            #need to build the monsters randomly
            #with logic based on if number is > 0 or = 0
            self.build_encounter(SEED)
        
        else:
            #do a check on the length of the list
            #and on if the CR level matches the difficulty category
            if hasattr(CRs,'__iter__'):
                if NUMBER>0 and len(CRs)!=NUMBER:
                    raise ValueError('Mismatch between specified number \
                    of enemies ({NUMBER}) and number of challenge ratings \
                    passed in ({len(CRs)}).')
                
                else:
                    #the CRs variable should tell us
                    #the number of enemies, 
                    self.num_members=self.num_members \
                      if self.num_members>0 else len(CRs)
                    
            #calculate total XP and corresponding difficulty
            self.total_XP,difficulty_cat=calculate_difficulty(CRs,NUM_PCs,
                                                              LVL_PCs,True)
                    
        #make sure that the calculated difficulty matches
        #what the user requested, if they did
        if self.difficulty is not None and difficulty_cat!=self.difficulty:
            raise ValueError(f'Provided inputs give encounter difficulty of \
            "{difficulty_cat}", which does not match specified difficulty of \
            "{self.difficulty}".')
        
        #update the object variable, if necessary
        self.difficulty=difficulty_cat if self.difficulty is None \
          else self.difficulty
        
        #now we need to calculate an HP value if it was not specified
        if not HP>0:
            self.calculate_hp()
        	

    def valid_difficulty(self,DIFFICULTY):
        return DIFFICULTY.lower() in ['easy',
		    'medium','hard','deadly']
	
	#when no challenge rating info is supplied, build an encounter
	#based on either difficulty rating and/or number of enemies
	def build_encounter(self,SEED=None):
	    if self.num_members<=0 and self.difficulty is None:
	        raise ValueError('Cannot specify 0 enemies and None type for \
	        encounter difficulty.')
	    
	    #create a random number generator instance using the
	    #passed seed or the integer version of current unix timestamp
	    rng=np.random.default_rng(seed=SEED if SEED is not None \
	      else int(time.time()))
	    
	    #get the list of possible challenge ratings to choose from
	    possible_CRs=[key for key in CR_to_XP.keys()]
	    
	    #create an empty list to fill
	    enemies=[]
	    
	    #set a maximum number of enemies to control the while loop
	    #if num_members is 0, then set an unrealistically high number
	    num_max=self.num_members if self.num_members>0 else 100
	    
	    #now we want a limiting value based on the requested difficulty
	    if self.difficulty is not None:
	        boundaries=calculate_difficulty_boundaries(self.num_pcs,
	                                                    self.pc_levels)
	        
	        #quickly turn it into a dictionary for ease
	        idx=1 if self.difficulty='easy' else \
	            2 if self.difficulty='medium' else \
	            3
	        
	        XP_limit=boundaries[idx][1]
	        
	        #for a deadly encounter, this is somewhat open ended
	        #but let's make sure that it isn't more than twice the limit
	        #in case number of enemies was not specified
	        if self.difficulty=='deadly':
	            XP_limit*=2
	    
	    #continue adding as long as we haven't eliminated all
	    #possible CR values or met the requested number of enemies
	    while possible_CRs and len(enemies)<num_max:
	        #do stuff
	    
	    
	    return
	
	#if HP was not specified, calculate an HP total
	#based on challenge ratings
	def calculate_hp()
	    
	    return
	    