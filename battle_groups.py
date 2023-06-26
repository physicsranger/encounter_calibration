#this module will define a base BattleGroup class
#as well as derived classes for the Party and the Enemies

import numpy as np

import time

from encounter_utils import (
                    calculate_difficulty,
                    calculate_difficulty_boundaries,
                    CR_to_XP,
                    CR_ave_HP
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
    def __init__(self,LVL=1,EXTRAS=5,NUMBER=5,ATK=5,AC=13,HP=8.5):
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
        
    def current_hit_point_fraction(self):
        return self.hit_points/self.__max_hit_points
    
    def current_extras_fraction(self):
        return self.extras/self.__max_extras
    
    def max_hit_points(self):
        return self.__max_hit_points
    
    def max_extras(self):
        return self.__max_extras

class Enemies(BattleGroup):
    def __init__(self,DIFFICULTY,NUMBER=0,ATK=3,AC=13,HP=0,CRs=None,\
      NUM_PCs=5,LVL_PCs=1,SEED=None):
        #force this for now
        LVL_PCs=1
        
        if DIFFICULTY is None and NUMBER<=0 and CRs is None:
            raise ValueError('Cannot have non-positive number of enemies, \
            None-type for challenge ratings, and None-type for difficulty.')
        
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
        
        if self.challenge_ratings is None or self.num_members<=0:
            #need to build the monsters randomly
            #with logic based on if number is > 0 or = 0
            self.build_encounter(SEED)
        
        else:
            #do a check on the length of the list
            #and on if the CR level matches the difficulty category
            if hasattr(self.challenge_ratings,'__iter__'):
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
	    if self.challenge_ratings is None:
	        possible_CRs=[key for key in CR_to_XP.keys()]
	    elif hasattr(self.challenge_ratings,'__iter__'):
	        possible_CRs=[CR for CR in self.challenge_ratings]
	    else:
	        possible_CRs=[self.challenge_ratings]
	    
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
	        idx=1 if self.difficulty=='easy' else \
	            2 if self.difficulty=='medium' else \
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
	        #randomly select a challenge rating for a possible new enemy
	        new_enemy=rng.choice(possible_CRs,1)[0]
	        
	        #if we have a target difficulty
	        if self.difficulty is not None:
    	        #check if that pushes us past the XP_limit
	            this_XP=calculate_difficulty(enemies+[new_enemy],
	                                         self.num_pcs,
	                                         self.pc_levels,
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
	    
	    #now finish up and set the total_XP attribute
	    #and update the difficulty rating if it wasn't specified
	    self.total_XP,difficulty=calculate_difficulty(enemies,
	                                             self.num_pcs,
	                                             self.pc_levels)
	    	    
	    self.difficulty=difficulty if self.difficulty is None else \
	                    self.difficulty
	    
	    self.challenge_ratings=enemies if self.challenge_ratings is None \
	                    else self.challenge_ratings
	    
	    if self.num_members<=0:
	        self.num_members=len(enemies)
	    
	
	#if HP was not specified, calculate an HP total
	#based on challenge ratings
    def calculate_hp(self):
        if hasattr(self.challenge_ratings):
            self.hit_points=sum([CR_ave_HP.get(CR) \
	                            for CR in challenge_ratings])
	    
        else:
	        self.hit_points=\
	            self.num_members*CR_ave_HP.get(self.challenge_ratings)
	    