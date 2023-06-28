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
                      'pc_down_threshold':self.party.hit_points/2,
                      'enemies_down_threshold':self.enemies.hit_points/2
                      'concluded':False}
        
        while not round_results.get('concluded'):
            
            round_results=self.run_round(round_results)
        
        #now the encounter is over, anything else to do?
        #let's put everything of note in a dictionary for ease
        #of access after the fact
        self._make_summary()
    
    def _make_summary(self):
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
                      'frac_enemies_down':\
                        self.num_enemies_down()/self.enemies.num_members}
            
    
    def run_round(self,round_status):
        for idx,combatant in enumerate(self.initiative_order):
            if not self.combatant_down[idx]:
                round_statuts.update(\
                  [('party_damage',
                  self.run_turn(combatant,round_status.get('party_damage')))])
                
                round_status.update(\
                  [('pc_down_threshold',
                     self.check_down_pc(round_status\
                       .get('pc_down_threshold')))])
                
                round_status.update(\
                  [('enemies_down_threshold',
                     self.check_down_enemy(round_status\
                       .get('enemies_down_threshold')))])
                
                #let's construct a lot of logic to know if we need to
                #break out of the loop, try to catch all possibilities
                
                if self.encounter_over():
                    break
        
        round_results={'party_damage':round_status.get('party_damage'),
          'pc_down_threshold':round_status.get('pc_down_threshold'),
          'enemy_down_threshold':round_status.get('enemy_down_threshold'),
          'concluded':self.encounter_over()}
        
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
                    
                    #now check if a PC was down, assume the healing
                    #got them back up from 0, not currently working with
                    #death (e.g., failed death saves or massive damage)
                    if self.num_pcs_down()>0:
                        self.pc_back_up()
                    
                else:
                    use_extra=self.rng.binomial(1,0.1)
                    self.party.extra-=use_extra
            
            else:
                use_extra=0
            
            if not healed:        
                d20=self.rng.randint(1,21)
                    
                ##if d20==20:
                    ##damage=self.party.average_damage*(1+use_extra)*2
                    
                if d20>1 and \
                  (d20+self.party.to_hit>=self.enemies.armor_class \
                  or d20==20):
                    #if meet or beat armor class (or nat 20), a hit
                    #use average damage, x2 if using an extra and then
                    #x2 again if natural 20 (yes, this isn't exactly correct)
                    damage=self.party.average_damage*(1+use_extra)\
                      *(1+int(d20==20))
                    
                else:
                    damage=0
                    
                self.enemies.hit_points-=damage
                    
            return party_damage             
        
        else:
            #assume no healing or extras at this level
            d20=self.rng.randint(1,21)
            
            if d20>1 and \
               (d20+self.enemies.to_hit>=self.party.armor_class \
               or d20==20):
               damage=self.enemies.average_damage*(1+int(d20==20))
            
            else:
                damage=0
            
            self.party.hit_points-=damage
            
            party_damage+=damage
            
        return party_damage
    
    def check_down_pc(self,down_threshold):
        if self.party.hit_points<=down_threshold:
            self.down_pc()
            
            down_threshold=self.update_pc_down_threshold()
        
        return down_threshold
    
    def check_down_enemy(self,down_threshold):
        if self.enemies.hit_points<=down_threshold:
            self.down_enemy()
            
            down_threshold=self.update_enemies_down_threshold()
        
        return down_threshold
    
    def down_pc(self):
        up_pcs=(self.initiative_order)&(~self.combatant_down)
        up_pcs_idx=[idx for idx,flag in enumerate(up_pcs) if flag]
        
        #make sure we have a non-empty list
        if up_pcs_idx:
            #randomly pick an up PC to knock out
            down_idx=self.rng.choice(up_pcs_idx,size=1)
            
            self.combatant_down[down_idx]=1
    
    def down_enemy(self):
        up_enemies=(self.initiative_order==0)&(~self.combatant_down)
        up_enemies_idx=[idx for idx,flag in enumerate(up_enemies) if flag]
        
        #make sure we have a non-empty list
        if up_enemies_idx:
            #randomly pick an up enemy to known out
            down_idx=self.rng.choice(up_enemies_idx,size=1)
            
            self.combatant_down[down_idx]=1
    
    def update_pc_down_threshold(self):
        num_pcs=self.party.num_members-self.num_pcs_down()
        return 0 if num_pcs<=0 else \
          self.party.hit_points//num_pcs
    
    def update_enemies_down_threshold(self):
        num_enemies=self.enemies.num_members-self.num_enemies_down()
        return 0 if num_enemies<=0 else \
          self.enemies.hit_points//num_enemies
    
    def num_pcs_down(self):
        return sum(self.initiative_order[self.combatant_down==1])
    
    def num_enemies_down(self):
        return sum(self.initiative_order[self.combatant_down==1]==0)
    
    def pc_back_up(self):
        downed_pcs=(self.initiative_order)&(self.combatant_down)
        downed_pcs_idx=[idx for idx,flag in enumerate(downed_pcs) if flag]
        
        #make sure we don't have an empty list
        if downed_pcs_idx:
            #randomly select a pc to bring up
            up_idx=self.rng.choice(downed_pcs_idx,size=1)
            
            #set the combatant_down flag to 0 for the newly raised PCs
            self.combatant_down[up_idx]=0
    
    #logic to check if encounter is over
    #much of it should be redundant, but let's just be
    #extra careful for now
    def encounter_over(self):
        #are all PCs down?
        all_pcs_down=self.party.num_members==self.num_pcs_down()
        
        #are all enemies defeated?
        all_enemies_down=self.enemies.num_members==self.num_enemies_down()
        
        #is the party HP at 0?
        party_zero_hp=self.party.hit_points<=0
        
        #do the enemies have 0 HP?
        enemies_zero_hp=self.enemies.hit_points<=0
        
        return all_pcs_down or all_enemies_down or party_zero_hp or enemies_zero_hp
        