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
                    CR_to_float,
                    valid_difficulty
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
        
        #should do a check on the lengths of the lists
        
        #set the to hit value either rounding or averaging
        #first and then rounding
        if hasattr(ATK,'__iter__'):
            self.to_hit=np.round(sum(ATK)/len(ATK))
        else:
            self.to_hit=ATK
        
        #do the same for the armor class
        if hasattr(AC,'__iter__'):
            self.armor_class=np.round(sum(AC)/len(AC))
        else:
            self.armor_class=AC
        
        #quick check on the resulting armor_class value
        if self.armor_class<0:
            raise ValueError(f'Average armor class of battle group\
 must be non-negative, calculated AC = {self.armor_class}')
        
        #either sum up the input HP or multiply the 
        #input value by the number of members
        #and then round in both cases
        if hasattr(HP,'__iter__'):
            self.hit_points=round(sum(HP))
        else:
            self.hit_points=round(NUMBER*HP)
        
        #quick check on the HP value
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
        the average damage used for all members of the party
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
    '''
    class for the enemy group, inherits from BattleGroup class
    
    ...
    
    Attributes
    ----------
    average_damage - int
        the average damage used for all enemies upon a successful hit
    challenge_ratings - str or list
        the challenge rating for all enemies or a list of challenge
        ratings, one per group member
    difficulty - str
        the difficulty rating for this enemy group, based on the
        challenge_ratings, num_pcs, and pc_levels
    num_pcs - int
        the number of PCs for which this enemy group's difficulty
        rating is to be calculated/compared against
    pc_levels - int or list
        the level(s) of the PCs for which this enemy group's difficulty
        rating is to be calculated/compared against, currently this
        is forced to be 1, but future updates may add functionality for
        higher levels and a mix of levels
    total_xp - float
        the total experience points of the encounter, incorporating
        challenge_ratings and modifiers which depend on the
        num_pcs and num_members values
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
    
    Methods
    -------
    build_enemy_group(SEED=None)
        a method to build the enemy group when no challenge rating
        information is supplied based on the number of enemies
        and/or the target difficulty level
    calculate_hp()
        method to calculate the group total hit points, based on
        challenge_ratings, if no average value(s) given as input,
        will be rounded to an int
    calculate_to_hit()
        method to calculate the group average to hit bonus, based
        on challenge_ratings, if no average value(s) given as input,
        will be rounded to an int
    get_average_damage()
        a method to assign the average damage attribute for the
        group based on the challenge_ratings
    _add_enemies(possible_CRs,rng=None)
        method called by build_enemy_group to construct candidate
        enemy group based on number of enemies and/or target
        difficulty, returned group is evaluated for compliance
        before being accepted
    '''
    
    def __init__(self,DIFFICULTY,NUMBER=0,ATK=3,AC=13,HP=0,CRs=None,\
      NUM_PCs=5,LVL_PCs=1,SEED=None):
        '''
        Parameters
        ----------
        DIFFICULTY - str or None-type
            desired encounter difficulty, can be None-type if enemy
            number and/or challenge ratings are supplied, acceptable
            inputs are: easy, medium, hard, or deadly
            capitalization does not matter
        NUMBER - int
            number of enemies to populate the group with
        ATK - float or list
            average to hit bonus, or list of values to be averaged,
            used for each group member in encounters, will be rounded
            to an int
        AC - float or list
            average armor class, or list of values to be averaged, used
            for each group member in encounters, will be rounded to
            an int
        HP - float or list
            number of hit points per group member, or list of values
            to be summed, for the total group hit points, will be
            rounded to an int
        CRs - str or list or None-type
            challenge rating(s) of enemies in the group, can be a
            None-type in which case they will be determined randomly
            according to NUMBER and DIFFICULTY constraints,
            acceptable values are: '0', '1/8', '1/4', '1/2', '1',
            '2', or '3'
        NUM_PCs - int
            the number of PCs for which the encounter difficulty of
            this enemy group is calibrated for
        LVL_PCs - int or list
            the level(s) of PCs for which the encounter difficulty of
            this enemy group is calibrated, currently this is forced
            to a value of 1, but future updates may allow for higher
            levels and a mix of values
        SEED - int or None-type
            the random seed to be used when enemy groups are built randomly
            to match NUMBER and DIFFICULTY constraints, set for 
            reproducibility purposes and to avoid duplication if running
            many simulations with multiprocessing
        '''
    
        #force this for now
        LVL_PCs=1
        
        #check for invalid combination of inputs
        if DIFFICULTY is None and NUMBER<=0 and CRs is None:
            raise ValueError('Cannot have non-positive number of enemies,\
 None-type for challenge ratings, and None-type for difficulty.')
        
        #ensure that requested difficult is valid
        if DIFFICULTY is not None and not valid_difficulty(DIFFICULTY):
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
        
        #if we did not specify challenge ratings or the number
        #of group members, build the group randomly to match
        #the difficulty rating
        if self.challenge_ratings is None or self.num_members<=0:
            #need to build the monsters randomly
            #with logic based on if number is > 0 or = 0
            self.build_enemy_group(SEED)
        
        else:
            #do a check on the length of the list
            #and on if the CR level matches the difficulty category
            if hasattr(self.challenge_ratings,'__iter__') and \
              not isinstance(self.challenge_ratings,str):
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
	
	#when no challenge rating info is supplied, build an enemy group
	#based on either difficulty rating and/or number of enemies
    def build_enemy_group(self,SEED=None):
        '''
        method to randomly generate an enemy group when no
        challenge rating information is supplied, subject to 
        num_members and/or difficulty constraints
        
        Parameters
        ----------
        SEED - int or None-type
            random seed to be used to initialize the
            random number generator
        '''
        
        #quick check to make sure at least one of num_members
        #or difficulty is specified with a useful value
        if self.num_members<=0 and self.difficulty is None:
            raise ValueError('Cannot specify 0 enemies and None-type for\
 encounter difficulty.')
	    
        #create a random number generator instance using the
        #passed seed or the integer version of current unix timestamp
        rng=np.random.default_rng(seed=SEED if SEED is not None \
          else int(time.time()))
	    
	    #get the list of possible challenge ratings to choose from
	    #want it to be a list for ease of manipulation later
        if self.challenge_ratings is None:
            possible_CRs=[key for key in CR_to_XP.keys()]

        elif hasattr(self.challenge_ratings,'__iter__') and \
          not isinstance(self.challenge_ratings,str):
            possible_CRs=[CR for CR in self.challenge_ratings]

        else:
            possible_CRs=[self.challenge_ratings]
	    
	    #set a boolean variable to control when we exit
	    #the while loop
        success=False
	    
        while not (success or not possible_CRs):
	        #randomly generate a group of enemies
            enemies=self._add_enemies(possible_CRs,rng)
        
            #calculate the total_XP for the potential group
	        #update the difficulty rating if it wasn't specified
            total_XP,difficulty_cat=calculate_difficulty(enemies,
                                                 self.num_pcs,
                                                 self.pc_levels)
	        
	        #check that the returned difficulty actually matches
	        #what is requested, might not happen if we have a high 
	        #difficulty but low number of enemies, in which case
	        #we selectively remove the lowest challenge rating and
	        #try again
            if self.difficulty is not None and \
              self.difficulty!=difficulty_cat:
                low_idx=np.array([CR_to_float(CR) for CR in possible_CRs]).argmin()
                possible_CRs.remove(possible_CRs[low_idx])
	        
            else:
                success=True
	    
	    #with a final group decided on, set the total_XP attribute
        self.total_XP=total_XP
	    
	    #final check that the difficulty matches
        if self.difficulty!=difficulty_cat:
            print(f'Could not meet difficulty {self.difficulty} requirement\
 with only {self.num_members} enemies')
            return None
	    
	    #update attributes
        self.difficulty=difficulty if self.difficulty is None else \
	                    self.difficulty
	    
        self.challenge_ratings=enemies if self.challenge_ratings is None \
	                    else self.challenge_ratings
	    
        if self.num_members<=0:
	        self.num_members=len(enemies)
	
    def _add_enemies(self,possible_CRs,rng=None):
        '''
        method to randomly create an enemies group, selecting from
        a list of possible challenge ratings and subject to the 
        num_members and/or difficulty constraints
        
        Parameters
        ----------
        possible_CRs - list
            a list of strings corresponding to possible challenge
            rating values for enemies to be added to the group
        rng - numpy.random.default_rng instance or None-type
            random number generator instance for random selection
        
        Returns
        -------
        list
            list of challenge ratings (strings) corresponding to
            the members of the proposed enemies group
        '''
        
	    #create an empty list to fill
        enemies=[]
	    
    	#check on the random number generator
        if rng is None:
            rng=np.random.default_rng(seed=int(time.time()) if SEED is None else SEED)
    	
	    #set a maximum number of enemies to control the while loop
	    #if num_members is 0, then set an unrealistically high number
        num_max=self.num_members if self.num_members>0 else 20

        #now we want a limiting value based on the requested difficulty
        if self.difficulty is not None:
            boundaries=calculate_difficulty_boundaries(self.num_pcs,
	                                                   self.pc_levels)
	        
	        #based on how the previous function structures the returned
	        #list, we know which index we want for which difficulty rating
	        #may decide on a slicker way to do this in the future
            idx=1 if self.difficulty=='easy' else \
                2 if self.difficulty=='medium' else \
                3
	        
	        #the idx value will give us the upper limit
	        #unless the encounter is deadly, in which case we'll
	        #just set it high
            XP_max_limit=boundaries[idx][1]*3 if \
                self.difficulty=='deadly' else \
                boundaries[idx][1]
            
            #get the minimum value as the next index down
            #for medium and hard, 0 for easy, and the actual
            #idx value for deadly
            XP_min_limit=0 if idx==1 else \
                boundaries[idx][1] if self.difficulty=='deadly' else \
                boundaries[idx-1][1]
	            
    	
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
                if this_XP<XP_max_limit:
                    enemies.append(new_enemy)
	         
                #otherwise, remove the new_enemy challenge rating from
                #our choices as it will increase the value too much
                else:
                    possible_CRs.remove(new_enemy)
                
                #to make sure we don't always max out the
                #XP for a given difficulty, make it a 50/50 chance
                #that we exit early unless we have not met the
                #desired number of enemies (if specified)
                if this_XP>=XP_min_limit and this_XP<XP_max_limit \
                  and self.num_members<=0 and rng.binomial(1,0.5):
                  break
                
            else:
                enemies.append(new_enemy)
        
        return enemies
	
	#if HP was not specified, calculate an HP total
	#based on challenge ratings
    def calculate_hp(self):
        '''
        method to calculate the total hit points of the group
        from the challenge_ratings if the hit point per member
        was not specified upon object creation
        '''
        #if challenge_ratings is a list, iterate through
        #the list and sum the total hit points
        if hasattr(self.challenge_ratings,'__iter__') and \
          not isinstance(self.challenge_ratings,str):
            self.hit_points=sum([CR_ave_HP.get(CR) \
	                            for CR in self.challenge_ratings])
	    
	    #otherwise, multiply the single challenge rating by the
	    #number of members in the enemy group
        else:
	        self.hit_points=\
	            self.num_members*CR_ave_HP.get(self.challenge_ratings)
	
    def calculate_to_hit(self):
        '''
        method to calculate the average to hit bonus of the group
        from the challenge_ratings if it was not specified upon
        object creation
        '''
        
        #if challenge_ratings is iterable, iterate through the list
        #and average the result
        if hasattr(self.challenge_ratings,'__iter__') and \
          not isinstance(self.challenge_ratings,str):
            #with the currently available CR values, the to hit
            #is either +3 or +4 for CR '3'
            to_hit=[4 if CR=='3' else 3]
            
            self.to_hit=np.average(to_hit).round(0).astype(int)
       
        #otherwise, set it based on if it is '3' or less
        else:
            self.to_hit=4 if self.challenge_ratings=='3' else 3
    
    def get_average_damage(self):
        '''
        method to calculate the average damage per group member
        based on the challenge_ratings information
        '''
        
        #if challenge_ratings is iterable, go through and average
        #all the damage values
        if hasattr(self.challenge_ratings,'__iter__') and \
          not isinstance(self.challenge_ratings,str):
            self.average_damage=np.average(\
                [CR_ave_DMG.get(CR) for CR in self.challenge_ratings])\
                .round(0).astype(int)
        
        #otherwise, use the corresponding value for the given CR
        else:
            self.average_damage=CR_ave_DMG.get(self.challenge_ratings)