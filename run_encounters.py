#set of functions to run multiple encounters
#utilizing multiprocessing
#and save results in CSV file for analysis

import numpy as np
import pandas as pd
import multiprocessing as mp

from battle_groups import (
                    Party,
                    Enemies
                    )

from encounter import Encounter

from encounter_utils import valid_configuration

from pathlib import Path

import time
import os

import yaml

def generate_encounter_results(encounter_config,output_csv,
                               num_sims,num_jobs,SEED=None):
    '''
    function to run many simulations of an encounter of a
    specified difficulty level for a set number of PCs of
    specified level, can optionally specify the number of
    enemies
    
    Parameters
    ----------
    encounter_config - str or path-like
        name or path-like object for input yaml configuration
        file specifying encounter details
    output_csv - str or path-like
        name or path-like object for output CSV file with
        details of each simulated encounter
    num_sims - int
        number of simulations to run
    num_jobs - int
        number of parallel jobs to run
    SEED - int
        optional seed to instantiate the random number generator
        only needed for if reproducibility is desired
    '''
    
    #first, we'll make sure that the configuration exists
    #and has valid options
    if not valid_configuration(encounter_config):
        raise RuntimeError(f'{encounter_config} has invalid parameters')
    
    #make sure a valid difficulty category has been supplied
    if not valid_difficulty(difficulty):
        raise ValueError(f'{difficulty = } is not valid, must be one\
 of "easy", "medium", "hard", or "deadly".  Case does not matter.')
    
    #make lists of SEEDs to give to each simulation
    #to avoid duplication and give each the name
    #of the pickle file
    rng=np.random.default_rng(seed=SEED \
      if SEED is not None \
      else int(time.time()))
    
    seeds=[int(time.time()*rng.random_sample()) \
            for _ in range(num_sims)]
    
    config_files=[str(encounter_config)]*num_sims

    inputs=np.array([seeds,config_files],dtype=object).T
    
    #create a multiprocessing pool and 'submit the jobs'
    with mp.Pool(processes=num_jobs) as pool:
        results=pool.map(simulate_encounter,inputs)
    
    #now write the output_csv
    encounter_df=pd.DataFrame(results)
    
    #let's recode the success column to be binary 0/1
    #instead of True/False which will likely be saved as a string
    encounter_df.success=encounter_df.success.astype(int,copy=True)
    
    #now, write to CSV file
    encounter_df.to_csv(output_csv,index=False)


def simulate_encounter(inputs):
    '''
    function to run a simulation of a given encounter
    and return details of the outcome
    
    Parameters
    ----------
    inputs - iterable
        must be of length 2 with the first element being an
        integer to use as the random seed and the second
        being the name of a YAML configuration file
    
    Returns
    -------
    dict
        Encounter class object summary dictionary
    '''
    
    #get simulation parameters from the pickled file
    with Path(inputs[1]).open('r') as cfile:
        config=yaml.safe_load(cfile)
    
    #create a random number generator instance using the
    #input seed value
    rng=np.random.default_rng(seed=inputs[0])
    
    #make the Party BattleGroup of PCs
    party=Party(LVL=config.get('pcs_level'),
                EXTRAS=config.get('extras'),
                NUMBER=config.get('num_pcs'),
                ATK=config.get('pcs_ATK'),
                AC=config.get('pcs_AC'),
                HP=config.get('pcs_HP'))
    
    #make the Enemies BattleGroup, give it a SEED
    #derived from the input SEED
    enemy_seed=int(inputs[0]*1000*rng.random_sample())
    
    CRs=None if config.get('CRs')=='None' else confg.get('CRs')
    
    enemies=Enemies(DIFFICULTY=config.get('difficulty'),
                    NUMBER=config.get('num_enemies'),
                    ATK=config.get('enemies_ATK'),
                    AC=config.get('enemies_AC'),
                    CRs=CRs,
                    NUM_PCs=config.get('num_pcs'),
                    LVL_PCs=config.get('pcs_level'),
                    SEED=enemy_seed)
    
    #check for an input initiative order
    initiative=None if config.get('initiative')=='None' \
      else config.get('initiative')
    
    #create a random seed for the encounter
    encounter_seed=int(inputs[0]*5000*rng.random_sample())
    
    #create the encounter
    encounter=Encounter(party=party,
                        enemies=enemies,
                        SEED=encounter_seed,
                        initiative=initiative)
    
    #run the encounter
    encounter.run_encounter()
    
    #return the summary dictionary
    return encounter.summary
    