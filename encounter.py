#class with methods to actually run the encounters
#needs Party and Enemies objects as inputs

import time

import numpy as np

class Encounter():
    '''
    class to run a simulated encounter between a Party
    BattleGroup and an Enemies BattleGroup
    
    ...
    
    Attributes
    ----------
    <initial>
    enemies - Enemies
        the Enemies BattleGroup subclass object representing
        the enemies
    heal_threshold - float
        when party has taken this much damage or more, a heal action
        is taken if enough extras remain to the party, value is updated
        as the encounter progresses
    initiative - numpy.ndarray
        turn order for combat, a 1 means party member takes a turn
        and a 0 means an enemy takes a turn
    party - Party
        the Party BattleGroup subclass object representing
        the PCs
    rng - numpy.random.default_rng
        random number generator used for the encounter
    seed - int
        random seed used to instantiate the random number generator
    <subsequent>
    combatant_down - numpy.ndarray
        array with 0/1 flag indicating if each combatant with the same
        index in initiative is down (1) or active (0)
    num_rounds - int
        number of rounds encounter took to complete, note that this
        will always round up (e.g., if a round ended after only 1 out
        of 5 turns, that will count as a full round)
    num_turns - int
        number of total turns encounter took to complete, only counts
        turns for a combatant is active
    summary - dict
        dictionary with the results of the encounter, with keys
          party_hp: ending total hit points of the party
          party_extras: ending total extras of the party
          frac_party_hp: ending total hit points of the party as
            a fraction of the max party hit points
          frac_party_extras: ending total extras of the party as
            a fraction of the max number of extras
          num_party_down: number of party members down at the end
            of the encounter
          frac_party_down: fraction of party member down at the end
            of the encounter
          success: boolean flag indicating if the party won the
            encounter or not
          enemies_hp: hit points of enemies group at the end of
            the encounter
          num_enemies_down: number of enemies down at the end of
            the encounter
          frac_enemies_down: fraction of enemies down at the end
            of the encounter
          num_rounds: number of rounds, always rounded up, that the
            encounter took to finish
          num_turns: number of turns, not counting downed combatant
            turns, the encounter took to finish
    
    Methods
    -------
    check_down_enemy(down_threshold)
        a method to evaluate if, after damage is dealt to the enemies,
        the threshold has been met to consider an enemy to be down
    check_down_pc(down_threshold)
        a method to evaluate if, after damage is dealt to the party,
        the threshold has been met to consider a PC to be down
    down_enemy()
        a method to randomly select an active enemy to be down
    down_pc()
        a method to randomly select an active PC to be down
    encounter_over()
        method to evaluate if the encounter should be considered
        over based on a few basic checks
    num_enemies_down()
        a method to calculate the number of enemies currently down
    num_pcs_down()
        a method to calculate the number of PCs currently down
    pc_back_up()
        a method to randomly activate a down PC as the resulting
        of healing
    run_encounter()
        method to run the encounter, handling rounds and turns via
        calls to other class methods
    run_round(round_status)
        method to run a round of combat, keeping track of a status
        dictionary
    run_turn(PC,party_damage)
        method to determine the outcome of a turn in a combat round
        with different rules for a PC turn or enemy turn, updates
        the amount of damage the party has taken since last heal
    set_initiative_order()
        method to randomly generate initiative (turn) order
    update_enemy_down_threshold()
        method to update the damage threshold for considering 
        another enemy to be down
    update_pc_down_threshold()
        method to update the damage threshold for considering
        another PC to be down
    _make_summary()
        method to create the summary attribute, a dictionary with
        information about a completed encounter
    
    '''
    
    def __init__(self,party,enemies,SEED=None,RNG=None,initiative=None):
        '''
        Parameters
        ----------
        party - Party BattleGroup subclass
            the Party class object representing the PCs, see the
            battle_groups module for more information
        enemies - Enemies BattleGroup subclass
            the Enemies class object representing the enemies, see
            the battle_groups module for more information
        SEED - int or None-type
            seed to instantiate the random number generator, if not
            specified will use the the system unix timestamp cast as
            an int, only used if RNG is None-type
        RNG - numpy.random.default_rng or None-type
            random number generator for the battle or a None-type which
            indicates that one is made using SEED
        initiative - iterable or None-type
            the initiative order, with PC turns represented by 1s and
            enemy turns represented by 0s, if not specified will be
            determined randomly
        '''
        
        self.party=party
        self.enemies=enemies
        
        #set an initial heal threshold for the party, when the enemies
        #have done at least this much damage a party member
        #will use an extra, if any are left, to heal
        self.heal_threshold=2*(self.party.hit_points/self.party.num_members) \
            if self.party.num_members>1 else 0.5*self.party.hit_points
        
        if RNG is None:
            #allow for setting random seed
            self.seed=int(time.time()) if SEED is None else SEED
        
            #assign a random number generator to the encounter
            self.rng=np.random.default_rng(seed=self.seed)
        
        else:
            self.rng=RNG
        
        #if not supplied as an input, randomly create
        #the initiative order
        if initiative is None:
            self.set_initiative_order()
        
        else:
            #do some sanity checks on the input order
            #first, make sure it has the correct number of
            #entires
            if len(initiative)!=\
              self.party.num_members+self.enemies.num_members:

                raise ValueError(f'Input initiative order does not have\
 the correct number of total entries, received {len(initiative)} but need\
 {self.party_num_members+self.enemies.num_members}')
            
            #next, make sure it only contains 0s and 1s
            if sum([turn!=0 and turn!=1 for turn in initiative])>0:

                    raise ValueError('Input initiative order should only\
 have entries of either 0 or 1.')
            
            #finally, make sure that all the 1s sum to the correct
            #value (i.e., the number of PCs)
            if sum(initiative)!=self.party.num_members:

                raise ValueError(f'Input initiative order does not have\
 correct number of PCs and enemies, should sum to {self.party.num_members}\
 but input values yield {sum(initiative)}')
            
            #if we get here, then everything should be okay
            #cast the iterable as a numpy array
            self.initiative_order=np.array(initiative)
    
    def set_initiative_order(self):
        '''
        method to randomly generate the initiative order, an array
        of 1s (PCs turn) and 0s (enemies turn)
        '''
        
        #get the correct number of 1s and 0s
        combatants=np.concatenate([np.ones(self.party.num_members),
                                   np.zeros(self.enemies.num_members)])
        
        #randomize
        self.initiative_order=self.rng.choice(combatants,size=combatants.shape,
                              replace=False)
    
    def run_encounter(self):
        '''
        method to run the encounter and create the
        summary attribute with results and details
        '''
        
        #create array for knowing if a combatant has been
        #removed from the battle
        self.combatant_down=np.zeros(len(self.initiative_order))
        
        #create attributes for tracking number of rounds and turns
        self.num_rounds=0
        self.num_turns=0
        
        #use this to keep track of values and whether or not
        #the encounter is finished
        round_results={'party_damage':0,
                      'pc_down_threshold':self.party.hit_points/2 if \
                        self.party.num_members>1 else 0,
                      'enemies_down_threshold':self.enemies.hit_points/2 if \
                        self.enemies.num_members>1 else 0,
                      'concluded':False}
        
        #start a while loop for the rounds
        while not round_results.get('concluded'):
            
            round_results=self.run_round(round_results)
            
            #always increment the number of rounds, even if
            #it may have ended early
            self.num_rounds+=1
        
        #create the encounter summary
        self._make_summary()
    
    def _make_summary(self):
        '''
        method to create the summary attribute, a dictionary with
        the results and details of a completed encounter
        '''
        
        #we want to be able to return the challenge ratings
        #but not comma separated
        if isinstance(self.enemies.challenge_ratings,str):
            CRstring=self.enemies.challenge_ratings
        
        else:
            CRstring='_'.join(self.enemies.challenge_ratings)
        
        #dictionary for ease of access to results
        #may rethink logic for 'success' key value
        self.summary={'party_hp':self.party.hit_points,
                      'party_extras':self.party.extras,
                      'frac_party_hp':\
                        self.party.current_hit_point_fraction(),
                      'frac_party_extras':\
                        self.party.current_extras_fraction(),
                      'num_party_down':self.num_pcs_down(),
                      'frac_party_down':\
                        self.num_pcs_down()/self.party.num_members,
                      'success':not self.party.hit_points<=0,
                      'enemies_hp':self.enemies.hit_points,
                      'num_enemies_down':self.num_enemies_down(),
                      'num_enemies':self.enemies.num_members,
                      'frac_enemies_down':\
                        self.num_enemies_down()/self.enemies.num_members,
                      'CRs':CRstring,
                      'totalXP':self.enemies.total_XP,
                      'num_rounds':self.num_rounds,
                      'num_turns':self.num_turns}
            
    
    def run_round(self,round_status):
        '''
        method to run a round of combat
        
        Parameters
        ----------
        round_status - dict
            a dictionary with keys denoting the current damage
            thresholds for downing a combatant of either party,
            a key denoting how much damage the party has taken
            since a heal, and a key with a flag to indicate if
            the encounter has concluded
        
        Returns
        -------
        dict
            and updated dictionary with the same keys as the input
            dictionary
        '''
        
        #cycle through the the combatants, skip if down, and
        #break early if encounter end conditions are met
        for idx,combatant in enumerate(self.initiative_order):
            #check if the current combatant is up
            if not self.combatant_down[idx]:
                #if they are, run the turn and update the damage
                #taken by the party since last heal
                round_status.update(\
                  [('party_damage',
                  self.run_turn(combatant,round_status.get('party_damage')))])
                
                #if combatant is 0, enemy, PC might need to be
                #considered down
                if not combatant:
                    round_status.update(\
                      [('pc_down_threshold',
                        self.check_down_pc(round_status\
                          .get('pc_down_threshold')))])
                
                #otherwise, see if an enemy should be
                #considered down
                else:
                    round_status.update(\
                      [('enemies_down_threshold',
                        self.check_down_enemy(round_status\
                         .get('enemies_down_threshold')))])
                
                #only count a turn if the combatant is active
                self.num_turns+=1
            
            #check if we've met end conditions
            #this most likely could be in the if statement
            #checking for an active combatant, but let's keep it
            #checked every turn to be safe
            if self.encounter_over():
                break
        
        #update the round_status by returning the round_results
        round_results={'party_damage':round_status.get('party_damage'),
          'pc_down_threshold':round_status.get('pc_down_threshold'),
          'enemies_down_threshold':round_status.get('enemies_down_threshold'),
          'concluded':self.encounter_over()}
        
        return round_results
    
    def run_turn(self,PC,party_damage):
        '''
        method to run a combatant turn in an encounter
        
        Parameters
        ----------
        PC - int
            indicator of if the active combatant is a PC (1)
            or an enemy (0)
        party_damage - int
            total damage currently taken by the party since
            the last heal action
        
        Returns
        -------
        int
            the updated party damage value
        '''
        
        #if the combatant is a PC
        if PC:
            #set a healed flag to false, tells us to skip
            #doing damage
            healed=False
            
            #check if the party has any extras left
            if self.party.extras>0:
                #if extras are left and party_damage is above
                #the heal threshold, perform a heal action
                if party_damage>=self.heal_threshold:
                    #reduce number of extras and increase
                    #hit points by average/typical value
                    self.party.extras-=1
                    self.party.hit_points+=5
                    
                    #reset the party_damage value and set healed flag
                    party_damage=0
                    healed=True
                    
                    #now check if a PC was down, assume the healing
                    #got them back up from 0, not currently working with
                    #death (e.g., failed death saves or massive damage)
                    if self.num_pcs_down()>0:
                        self.pc_back_up()
                
                #if we didn't meet the heal threshold, posit
                #that there is a 10% chance of using an extra
                #for more damage (spell slot, etc.)    
                else:
                    use_extra=self.rng.binomial(1,0.1)
                    self.party.extras-=use_extra
            
            #if no extras available, set value to 0 and move to damage
            else:
                use_extra=0
            
            #if we didn't heal, attempt to do damage
            if not healed:        
                #roll a d20
                d20=self.rng.integers(1,20,endpoint=True)
                
                #determine if the attack hits
                if d20>1 and \
                  (d20+self.party.to_hit>=self.enemies.armor_class \
                  or d20==20):
                    #if meet or beat armor class (or nat 20), a hit
                    #use average damage, x2 if using an extra and then
                    #x2 again if natural 20 (yes, this isn't exactly correct)
                    damage=self.party.average_damage*(1+use_extra)\
                      *(1+int(d20==20))
                
                #missed, no damage   
                else:
                    damage=0
                
                #update current hit point total of enemies and return  
                self.enemies.hit_points-=damage
                    
            return party_damage             
        
        #if the combatant is an enemy
        else:
            #assume no healing or extras at this level
            #so just roll a d20
            d20=self.rng.integers(1,20,endpoint=True)
            
            #check if the attack hits
            if d20>1 and \
               (d20+self.enemies.to_hit>=self.party.armor_class \
               or d20==20):
               damage=self.enemies.average_damage*(1+int(d20==20))
            
            #a miss, no damage
            else:
                damage=0
            
            #update current hit point total of party, update the
            #party_damage amount, and return
            self.party.hit_points-=damage
            
            party_damage+=damage
            
        return party_damage
    
    def check_down_pc(self,down_threshold):
        '''
        method to check if the current hit point total of
        the party is at or below the current threshold to
        down a random PC, if so, a PC is downed and the 
        threshold is updated
        
        Parameters
        ----------
        down_threshold - int
            the current value used to determine if a random
            PC needs to be considered down
        
        Returns
        -------
        float
            the updated down_threshold
        '''
        
        #check if the party is below the threshold
        if self.party.hit_points<=down_threshold:
            #down a random PC
            self.down_pc()
            
            #update the threshold
            down_threshold=self.update_pc_down_threshold()
        
        return down_threshold
    
    def check_down_enemy(self,down_threshold):
        '''
        method to check if the current hit point total of
        the enemies is at or below the current threshold to
        down a random enemy, if so, an enemy is downed and the 
        threshold is updated
        
        Parameters
        ----------
        down_threshold - int
            the current value used to determine if a random
            enemy needs to be considered down
        
        Returns
        -------
        float
            the updated down_threshold
        '''
        
        #check if the total enemies HP is below the threshold
        if self.enemies.hit_points<=down_threshold:
            #if so, down a random enemy
            self.down_enemy()
            
            #update the threshold
            down_threshold=self.update_enemy_down_threshold()
        
        return down_threshold
    
    def down_pc(self):
        '''
        method to randomly down an active PC
        '''
        
        #get an array with entries set to True if the
        #combatant is a PC and is active and get the
        #corresponding indices
        up_pcs=(self.initiative_order==1)&(self.combatant_down==0)
        up_pcs_idx=[idx for idx,flag in enumerate(up_pcs) if flag]
        
        #make sure we have a non-empty list
        if up_pcs_idx:
            #randomly pick an active PC to down
            down_idx=self.rng.choice(up_pcs_idx,size=1)[0]
            
            #update the combatant_down array
            self.combatant_down[down_idx]=1
    
    def down_enemy(self):
        '''
        method to randomly down an active enemy
        '''
        
        #get an array with entries set to True if the
        #combatant is an enemy and is active and get
        #the corresponding indices
        up_enemies=(self.initiative_order==0)&(self.combatant_down==0)
        up_enemies_idx=[idx for idx,flag in enumerate(up_enemies) if flag]
        
        #make sure we have a non-empty list
        if up_enemies_idx:
            #randomly pick an up enemy to known out
            down_idx=self.rng.choice(up_enemies_idx,size=1)[0]
            
            #update the combatant_down array
            self.combatant_down[down_idx]=1
    
    def update_pc_down_threshold(self):
        '''
        method to update the threshold used to determine if
        a PC should be downed
        
        Returns
        -------
        int
            the updated threshold
        '''
        
        #either set the threshold to 0 or the current
        #party total HP divided by the number of active
        #PCs, rounded down
        num_pcs=self.party.num_members-self.num_pcs_down()
        return 0 if num_pcs<=0 else \
          0 if num_pcs==1 else \
          self.party.hit_points//num_pcs
    
    def update_enemy_down_threshold(self):
        '''
        method to update the threshold used to determine if
        an enemy should be downed
        
        Returns
        -------
        int
            the udpated threshold
        '''
        
        #either set the threshold to 0 or the current
        #total enemy HP divided by the number of active
        #enemies, rounded down
        num_enemies=self.enemies.num_members-self.num_enemies_down()
        return 0 if num_enemies<=0 else \
          0 if num_enemies==1 else \
          self.enemies.hit_points//num_enemies
    
    def num_pcs_down(self):
        '''
        method to get the number of down PCs
        
        Returns
        -------
        int
            the number of down PCs
        '''
        
        return sum(self.initiative_order[self.combatant_down==1])
    
    def num_enemies_down(self):
        '''
        method to get the number of down enemies
        
        Returns
        -------
        int
            the number of down enemies
        '''
        
        return sum(self.initiative_order[self.combatant_down==1]==0)
    
    def pc_back_up(self):
        '''
        method to reactivate a random down PC
        '''
        
        #get an array of True if combatant is a PC and is down
        #and get the corresponding indices
        downed_pcs=(self.initiative_order==1)&(self.combatant_down==1)
        downed_pcs_idx=[idx for idx,flag in enumerate(downed_pcs) if flag]
        
        #make sure we don't have an empty list
        if downed_pcs_idx:
            #randomly select a PC to reactivate
            up_idx=self.rng.choice(downed_pcs_idx,size=1)[0]
            
            #set the combatant_down flag to 0 for the newly raised PC
            self.combatant_down[up_idx]=0
    
    def encounter_over(self):
        '''
        method to check if any of the encounter end conditions
        have been met
        
        Returns
        -------
        bool
            True if any end condition has been met, otherwise False
        '''
        
        #there is some redundancy in the conditions, but let's just
        #be extra sure
        
        #are all PCs down?
        all_pcs_down=self.party.num_members==self.num_pcs_down()
        
        #are all enemies defeated?
        all_enemies_down=self.enemies.num_members==self.num_enemies_down()
        
        #is the party HP at 0?
        party_zero_hp=self.party.hit_points<=0
        
        #do the enemies have 0 HP?
        enemies_zero_hp=self.enemies.hit_points<=0
        
        return all_pcs_down or all_enemies_down or party_zero_hp or enemies_zero_hp
        