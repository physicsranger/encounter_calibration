#this module will define a base BattleGroup class
#as well as derived classes for the Party and the Enemies

class BattleGroup():
    '''
    doc string goes here
    '''
    def __init__(self,NUMBER,ATK=None,AC=None,HP=None):
        self.num_members=NUMBER
        self.to_hit=ATK
        self.armor_class=AC
        
        if hasattr(HP,'__iter__'):
            self.hit_points=round(sum(HP))
        else:
            self.hit_points=round(NUMBER*HP)

class Party(BattleGroup):
    def __init__(self,LVL=1,NUMBER=5,ATK=5,AC=13,HP=25/3):
        #force LVL to be 1, but we can remove
        #this later if we add capability
        LVL=1
        super().__init__(NUMBER,ATK,AC,HP)
        
        self.pc_level=LVL

class Enemies(BattleGroup):
    def__init__(self,DIFFICULTY,NUMBER,ATK=3,AC=13,HP=0):
        if not  self.valid_difficulty(DIFFICULTY):
            raise ValueError(f'Invalid encounter difficulty {DIFFICULTY}')
        
        super().__init__(*args,**kwargs)
        
        self.difficulty=DIFFICULTY
        
        if hasattr((ATK,AC,HP),'__iter__'):
        	

    def valid_difficulty(self,DIFFICULTY):
        return DIFFICULTY.lower() in ['easy',
		    'medium','hard','deadly']
	