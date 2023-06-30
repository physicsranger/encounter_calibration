#this module will define a base BattleGroup class
#as well as derived classes for the Party and the Enemies

import numpy as np

import time

from encounter_utils import (
                    calculate_difficulty,
                    calculate_difficulty_boundaries,
                    CR_to_XP,
                    CR_ave_HP,
                    CR_ave_DMG,
                    CR_to_float
                    )

###################
#define base class
###################

class BattleGroup():
    '''
    base class to represent a group in a battle/encounter
    
    ...
    
    Attributes
    ----------
    armor_class - int
        the average armor class value used for all members of
        the battle group when determining if an attack from a
        rival group hits
    hit_points - int
        the total number of hit points of the battle group,
        summing over all members
    num_members - int
        the number of combatants in the battle group
    to_hit - int
        the average to hit bonus used for all members of the battle
        group when determining if an attack hits a member of a rival
        group
    '''
    
    def __init__(self,NUMBER,ATK=None,AC=None,HP=None):
        '''
        Parameters
        ----------
        NUMBER - int
            number of members in the battle group
        ATK - float or list
            average to hit bonus, or a list of values, to use for
            all members in an encounter, will be rounded to an int
        AC - float or list
            average armor class, or a list of values, to use for
            all members in an encounter, will be rounded to an int
        HP - float or list
            average hit points, or a list of values, for each group
            member, will be summed and rounded to an int
        '''
        
        if NUMBER<0:
            raise ValueError(f'Number of members must be non-negative\
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
            raise ValueError(f'Average armor class of battle group\
 must be non-negative, calculated AC = {self.armor_class}')
        
        if hasattr(HP,'__iter__'):
            self.hit_points=round(sum(HP))
        else:
            self.hit_points=round(NUMBER*HP)
        
        if self.hit_points<0:
            raise ValueError(f'Total hit points of battle group\
 must be non-negative, calculated HP = {self.hit_points}')

##########################
#define class for the PCs
##########################

class Party(BattleGroup):
    '''
    class for the player characters (PCs) party, inherits
    from BattleGroup class
    
    ...
    
    Attributes
    ----------
    average_damage - int
        The average damage used for all members of the party
        upon a successful hit
    extras - int
        The number of extras available to the party, where
        an extra represents a spell slot or other 'consumable'
        which can increase damage or provide healing in battle
    pc_level - int or list
        The level(s) of the PCs.  Currently, this will be forced to 1
        (for first level), but future functionality may include the
        ability to use higher levels and a mix of different levels
    <inherited>
    armor_class - int
        the average armor class value used for all members of
        the battle group when determining if an attack from a
        rival group hits
    hit_points - int
        the total number of hit points of the battle group,
        summing over all members
    num_members - int
        the number of combatants in the battle group
    to_hit - int
        the average to hit bonus used for all members of the battle
        group when determining if an attack hits a member of a rival
        group
    <private>
    __max_hit_points - int
        the maximum hit point value of the party
    __max_extras - int
        the maximum number of extras of the party
    
    Methods
    -------
    current_extras_fraction()
        a method to return the current fraction of extras remaining
        to the party, in reference to the maximum number
    current_hit_point_fraction()
        a method to return the current fraction of hit points
        remaining to the party, in reference to the maximum value
    get_average_damage()
        a method to assign the average damage attribute for the
        party, currently a fixed number but future functionality
        may allow for variation
    max_extras()
        a method to access the value of the __max_extras attribute
    max_hit_points()
        a method to access the value of the __max_hit_points attribute
    '''
    
    def __init__(self,LVL=1,EXTRAS=5,NUMBER=5,ATK=5,AC=13,HP=8.5):
        '''
        Parameters
        ----------
        LVL - int or list
            level(s) of the PCs, currently this is forced to a value of
            1, but future updates may allow for different values and to
            supply a list with mixed levels
        EXTRAS - int
            the total number of extras, e.g., spell slots, items, abilities;
            which can grant boosts to damage or provide healing
        NUMBER - int
            the number of PCs in the party
        ATK - float or list
            the average to hit bonus, or a list of values to be
            averaged, to use for all PCs in an encounter, will be
            rounded to an int
        AC - float or list
            the average armor class, or a list of values to be averaged,
            to use for all PCs in an encounter, will be rounded to
            an int
        HP - float or list
            the average hit points, or a list of values to be averaged,
            to be summed and used as the party max hit point total, will
            be rounded to an int
        '''
        
        #force LVL to be 1, but we can remove
        #this later if we add capability
        LVL=1
        super().__init__(NUMBER,ATK,AC,HP)
        
        self.pc_level=LVL
        self.extras=EXTRAS
        
        self.get_average_damage()
        
        #set max values now so we don't forget
        #and can compare after a 'battle'
        self.__max_extras=EXTRAS
        self.__max_hit_points=self.hit_points
    
    def get_average_damage(self):
        '''
        method to calculate the average damage of the party,
        currently uses a fixed value but future updates may
        allow for more variability/customization
        '''
        
        #fixed for now, but set up a method
        #to allow for future functionality
        self.average_damage=7
    
    def current_hit_point_fraction(self):
        '''
        a method to return the current hit point total of
        the party as a fraction of the maximum total hit points
        '''
        
        return self.hit_points/self.__max_hit_points
    
    def current_extras_fraction(self):
        '''
        a method to return the current number of extras the 
        party has left as a fraction of the maximum total
        number they can have
        '''
        
        return self.extras/self.__max_extras
    
    def max_hit_points(self):
        '''
        a convenience method to access the value of the
        __max_hit_points attribute
        '''
        
        return self.__max_hit_points
    
    def max_extras(self):
        '''
        a convenience method to access the value of the
        __max_extras attribute
        '''
        
        return self.__max_extras

##############################
#define class for the enemies
##############################

class Enemies(BattleGroup):
    def __init__(self,DIFFICULTY,NUMBER=0,ATK=3,AC=13,HP=0,CRs=None,\
      NUM_PCs=5,LVL_PCs=1,SEED=None):
        #force this for now
        LVL_PCs=1
        
        if DIFFICULTY is None and NUMBER<=0 and CRs is None:
            raise ValueError('Cannot have non-positive number of enemies,\
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
                    raise ValueError('Mismatch between specified number\
 of enemies ({NUMBER}) and number of challenge ratings passed in ({len(CRs)}).')
                
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
                raise ValueError(f'Provided inputs give encounter difficulty of\
 "{difficulty_cat}", which does not match specified difficulty\
  of "{self.difficulty}".')
        
        #update the object variable, if necessary
        self.difficulty=difficulty_cat if self.difficulty is None \
          else self.difficulty
        
        #now we need to calculate an HP value if it was not specified
        if self.hit_points<=0:
            self.calculate_hp()
        
        if self.to_hit<=0:
            self.calculate_to_hit()
        
        self.get_average_damage()

    def valid_difficulty(self,DIFFICULTY):
        return DIFFICULTY.lower() in ['easy','medium','hard','deadly']
	
	#when no challenge rating info is supplied, build an encounter
	#based on either difficulty rating and/or number of enemies
    def build_encounter(self,SEED=None):
	    if self.num_members<=0 and self.difficulty is None:
	        raise ValueError('Cannot specify 0 enemies and None-type for\
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
	    
	    success=False
	    
	    while not success or not possible_CRs:
	        enemies=self._add_enemies(possible_CRs,rng)
	    
	        #now finish up and set the total_XP attribute
	        #and update the difficulty rating if it wasn't specified
	        total_XP,difficulty_cat=calculate_difficulty(enemies,
	                                             self.num_pcs,
	                                             self.pc_levels)
	        
	        #check that the returned difficulty actually matches
	        #what is requested, might not happen if we have a high 
	        #difficulty but low number of enemies
	        if self.difficulty is not None and \
	          self.difficulty!=difficulty_cat:
	            low_idx=np.array([CR_to_float(CR) for CR in possible_CRs]).argmin()
	            possible_CRs.remove(possible_CRs[low_idx])
	        
	        else:
	            success=True
	    
	    self.total_XP=total_XP
	    
	    #check that the difficulty matches
	    if self.difficulty!=difficulty_cat:
	        print(f'Could not meet difficulty {self.difficulty} requirement\
 with only {self.num_members} enemies')
	        return None
	    
	    self.difficulty=difficulty if self.difficulty is None else \
	                    self.difficulty
	    
	    self.challenge_ratings=enemies if self.challenge_ratings is None \
	                    else self.challenge_ratings
	    
	    if self.num_members<=0:
	        self.num_members=len(enemies)
	
    def _add_enemies(self,possible_CRs,rng=None):
	    #create an empty list to fill
        enemies=[]
	    
    	#check on the random number generator
        if rng is None:
            rng=np.random.default_rng(seed=int(time.time()) if SEED is None else SEED)
    	
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
                XP_limit*=4
    	
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
        
        return enemies
	
	#if HP was not specified, calculate an HP total
	#based on challenge ratings
    def calculate_hp(self):
        if hasattr(self.challenge_ratings,'__iter__'):
            self.hit_points=sum([CR_ave_HP.get(CR) \
	                            for CR in self.challenge_ratings])
	    
        else:
	        self.hit_points=\
	            self.num_members*CR_ave_HP.get(self.challenge_ratings)
	
    def calculate_to_hit(self):
        if hasattr(self.challenge_ratings,'__iter__'):
            to_hit=[4 if CR=='3' else 3]
            self.to_hit=np.average(to_hit).round(0).astype(int)
        else:
            self.to_hit=4 if self.challenge_ratings=='3' else 3
    
    def get_average_damage(self):
        if hasattr(self.challenge_ratings,'__iter__'):
            self.average_damage=np.average(\
                [CR_ave_DMG.get(CR) for CR in self.challenge_raings])\
                .round(0).astype(int)
        else:
            self.average_damage=CR_ave_DMG.get(self.challenge_ratings)