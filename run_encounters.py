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

from encounter_utils import (
                    valid_difficulty,
                    valid_challenge_ratings
                    )

from pathlib import Path

import time
import pickle

def generate_encounter_results(difficulty,output_csv,
                                num_sims,num_jobs=1,
                                num_pcs=5,pc_levels=1,
                                num_enemies=None,CRs=None,
                                SEED=None):
    '''
    function to run many simulations of an encounter of a
    specified difficulty level for a set number of PCs of
    specified level, can optionally specify the number of
    enemies
    
    Parameters
    ----------
    difficulty - str
        the desired difficulty category: easy, medium,
        hard, or deadly
    output_csv - str or path-like
        name or path-like object for output CSV file with
        details of each simulated encounter
    num_sims - int
        number of simulations to run
    num_jobs - int
        number of parallel jobs to run
    num_pcs - int
        number of PCs in each simulation
    pc_levels - int or list
        the level(s) of the PCs, currently this is forced to
        a value of 1, but future updates may allow for higher
        levels and a mix of values
    num_enemies - int or None-type
        optional number of enemies desired in the encounter
    CRs - str, list, or None-type
        optional challenge rating for all enemies or a list
        of possible challenge ratings to use
    SEED - int
        optional seed to instantiate the random number generator
        only needed for if reproducibility is desired
    '''
    
    #first, make sure a valid difficulty category has been supplied
    if not valid_difficulty(difficulty):
        raise ValueError(f'{difficulty = } is not valid, must be one\
 of "easy", "medium", "hard", or "deadly".  Case does not matter.')
    
    #if CRs was specified, check that the values are valid
    if CRs is not None:
        if not valid_challenge_ratings(CRs):
            raise ValueError(f'Invalid challenge rating(s) selection: {CRs}')
    
    #now setup the inputs for the simulations to run in parallel
    #dump the things that don't change into a pickled file
    tmp_path=Path.cwd()/'tmp'
    if not tmp_path.exists():
        remove_tmp=True
        tmp_path.mkdir()
    
    else:
        remove_tmp=False
    
    tmp_path/='encounter_sims.pkl'
    
    with tmp_path.open('wb') as tmp_file:
        pickle.dump(num_pcs,tmp_file)
        pickle.dump(pc_levels,tmp_file)
        pickle.dump(
    
    