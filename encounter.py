#class with methods to actually run the encounters
#needs Party and Enemies objects as inputs

import time

import numpy as np

class Encounter():
    def __init__(self,party,enemies,SEED=None,initiative=None):
        self.party=party
        self.enemies=enemies
        
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
        