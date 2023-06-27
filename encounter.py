#class with methods to actually run the encounters
#needs Party and Enemies objects as inputs

import time

import numpy as np

class Encounter():
    def __init__(self,party,enemies,SEED=None,initiative=None):
        self.party=party
        self.enemies=enemies
        
        self.heal_threshold=2*(self.party.hit_points/self.party.num_members)
        
        #allow for setting random seed
        self.seed=int(time.time() if SEED is None else SEED
        
        #assign a random number generator to the encounter
        self.rng=np.random.default_rng(seed=self.SEED)
        
        if initiative is None:
            self.set_initiative_order()
        else:
            #do some sanity checks on the input order
            if len(initiative)!=\
              self.party_num_members+self.enemies.num_members:
                raise ValueError(f'Input initiative order does not have\
 the correct number of entries, received {len(initiative)} but need\
 {self.party_num_members+self.enemies.num_members}')
            
            if sum(initiative)!=self.party.num_members:
                raise ValueError(f'Input initiative order does not have\
 correct number of PCs and enemies, should sum to {self.party.num_members}\
 but input values yield {sum(initiative)}')
            
            self.initiative_order=np.array(initiative)
        
        #store the starting initiative order for possible analysis
        #define method to access it, but this way we don't accidentally
        #overwrite it
        self.__starting_initiative=self.initiative_order.copy()
    
    #method to simply return the private variable with starting initiative
    def get_starting_initiative(self):
        return self.__starting_initiative.copy()
    
    #function to randomly assign initiative order
    def set_initiative_order(self):
        combatants=np.concatenate([np.ones(self.party.num_members),
                                   np.zeros(self.enemeis.num_members)])
        
        self.initiative_order=rng.choice(combatants,size=combatants.shape,
                              replace=False)
    
    #method to run the encounter, calling other methods
    #as it does so
    def run_encounter(self):
        #create array for knowing if a combatant has been
        #removed from the battle
        self.combatant_down=np.zeros(len(self.initiative_order))
        
        round_results{'party_damage':0,
                      'pc_drop_threshold':self.party.hit_points/2,
                      'enemies_drop_threshood':self.enemies.hit_points/2
                      'concluded':False}
        
        while not round_results.get('concluded'):
            
            round_results=self.run_round(round_results)
            
    
    def run_round(self,round_status):
        for idx,combatant in enumerate(self.initiative_order):
            if not self.combatant_down[idx]:
                round_statuts.update(\
                ['party_damage',
                  self.run_turn(combatant,round_status.get('party_damage'))])
                
                #now do stuff to determine if combatant is removed
                #and evaluate if we need to end the encounter
        
        
        
        round_results={'party_damage':round_status.get('party_damage'),
          'pc_drop_threshold':round_status.get('pc_drop_threshold'),
          'enemy_drop_threshold':round_status.get('enemy_drop_threshold'),
          'concluded':self.party.hit_points<=0 or self.enemies.hit_points<=0}
        
        return round_results
    
    def run_turn(self,PC,party_damage):
        if PC:
            healed=False
            if self.party.extras>0:
                if party_damage>=self.heal_threshold:
                    self.party.extras-=1
                    self.party.hit_points+=5
                    party_damage=0
                    healed=True
                else:
                    use_extra=self.rng.binomial(1,0.1)
                    self.party.extra-=use_extra
            
            else:
                use_extra=0
            
            if not healed:        
                d20=self.rng.randint(1,21)
                    
                if d20==20:
                    damage=self.party.average_damage*(1+use_extra)*2
                    
                elif d20>1 and \
                  d20+self.party.to_hit>=self.enemies.armor_class:
                
                    damage=self.party.average_damage*(1+use_extra)
                    
                else:
                    damage=0
                    
                self.enemies.hit_points-=damage
                    
            return party_damage             
        
        else:
            #doenemystuff
            
        return round_status