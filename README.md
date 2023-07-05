# D&D Encounter Difficulty Calibration

This repo is a set of scripts, simulated data, and results of analyzing said data with the aim of providing quantitative measures to evaluate encounters in the popular tabletop roleplaying game Dungeons and Dragons (D&D, 5e).

This was done as a personal project, building out my personal data science portfolio showing off some analysis skills.  The main goal was to have fun in something related to a pastime I enjoy and maybe provide a useful, different way to think about one aspect of the game.  I am not claiming to be an expert or authority on the matter, and not everyone is likely to agree with the simplifications and assumptions I have made.  Constructive feedback is welcomed and encouraged.

## The Problem

With a roleplaying game such as D&D, someone needs to design encounters for the player characters (PCs) to engage with.  These can be social encounters (convincing a local barkeep to confide important information, etc.) or combat encounters.  When building combat encounters, the game rules include mechanics to create scenarios of varying difficulty.  The mechanics classify encounters as 'easy', 'medium', 'hard', and 'deadly'.  The rules include useful, qualitative descriptions of these difficulty categories, and I'm not going to reproduce them here.  The rules also include some quantitative measures, such as the daily experience point (XP) budget characters of different levels can reasonably expect to manage.

When a dungeon master (DM) plans out their campaign, or even if they're using a pre-built module, they often plan for a serious of possible encounters and need to develop a sense for how taxing these will be on the PCs.  This sense develops over time as the DM runs many, many sessions.  However, I wondered if there was a way to get more quantitative general guidelines.

I could not find any data source covering the details of an encounter (party composition, resources, enemies) and the outcomes. I decided to make some via simple simulations.  There can be many, many unpredictable factors affecting the outcome of an encounter, far too many to try and anticipate and replicate in a simulation.  My thinking was, however, if certain simplifications and assumptions can be made (see next section), then looking at the behavior on average should still provide insight, which DMs might find useful in planning their gaming sessions.

## Simulation Design

The simulation is designed around the idea of an encounter consisting of two battle groups, the party of PCs and the enemies.  The code includes custom classes for the Party and Enemies, built off a base BattleGroup class.  These are inputs to a custom Encounter class which is used to run the combat.

This section of the README details the simplifications and assumptions made in the simulations.  Any conclusions drawn from the simulations are contingent upon the applicability of the assumptions and other simulation details.

### The PCs

The first major limitation of the simulation is that it only considers PCs of first level.  This choice was adopted for the sake of simplicity and the ability to complete a version within a reasonable amount of time.  First level players have fewer abilities and are much less likely, in general, to have magic items which can drastically tip the scales in their favor during a battle.  Additionally, it is reasonable to assume that they won't have deviated much from the starting equipment outlined in the class rules.

Each PC can be one of several 'classes', with different skills, hit points, special abilities, etc.  For simplification, the party hit points (HP) are tracked as a whole, as are 'extras', representing spell slots, limited-use abilities, etc.  Average values are used for the HP per party member, to hit bonus, and armor class values.  Also for ease, **PCs are not assigned a specific class**.

When considering PC abilities (strength, intelligence, etc.), there is too much variety in how these are determined.  Players can use premade sheets, use the point-buy system, or roll to determine values and assign them to ability scores.  The last option is also frequently modified by DMs who look to ensure that players have balanced (or at least not sub-par) sheets.  I took the approach of considering the possibilities under the point buy system and that players will tend to max out the abilities most-closely related to their class (**resulting in a +3**, when applicable).

For the average HP per party member, I looked at the hit die for each of the player classes in the core rules and took the average of the maximum of each.  Starting hit points, barring any racial bonus and/or feat, are the max value of the hit die plus the constitution (CON) modifier.  Most classes have a d8 for their hit die, so it is no surprise that the **average is 8.5**.  Inherent in this value is the assumption that all classes are equally likely to be chosen by players.  I'm sure that people will have strong assumptions about this, but given the number of classes using a d8 hit die, I think it is, at least, a good assumption to start with.

For the CON modifier, I opted to use a value of zero as some classes/players are likely to only ensure it isn't negative, others may want at least +1 or +2, and some players may accept a -1 in order to boost other stats.  The data files included in the repository assume an **average CON modifier of 0**, but users could adopt a different value and run their own simulations easily (see the Usage section and accompanying notebooks).

For the average PC armor class (AC), I took a similar approach of evaluating the starting equipment for each class and deriving possible values factoring in if the class has a choice in starting armor.  If dexterity (DEX) added to the AC of a given armor, an AC value was included for every reasonable value of DEX based on class (e.g., we can all assume the average rogue will build with a high DEX).  This resulted in an **average AC of 13**.

For the to hit bonus, I made the assumption that players will max this out to the extent possible so we assume a value of +3, and then add proficiency bonus of +2, to yield an **average to hit bonus of +5**.

I looked at all the weapons in the core game material and averaged their average damage rolls, with the expected +3 from ability scores.  I then looked at all damage dealing cantrips in the core material and did the same, without adding extra damage from ability scores.  Rounding down, this led to an **average damage per hit of 7**.

I chose to **not consider saving throws** for simplicity, as that would require considering the difficulty challenge (DC), the variation in bonus of the combatant(s) making the save, and the distribution of damage, half damage, or no damage.

Since I chose to consider only the total pool of party HP, the simulation starts with an initial 'down threshold' of half the total HP.  When the party's HP gets to or below this threshold, a random PC is designated as 'down' and the threshold is reset to be the current HP divided by the number of PCs still active. Any healing will bring a down PC up and **death saving throws** are not considered.

Looking at the first level abilities and resources of the different classes, I opted to have the **number of total party 'extras' be 5**.  This represents things such as spell slots, a paladin's lay on hands, etc.  Any of these extras can be used for healing or to try and do more damage.  A healing action is taken when the party receives damage surpassing a particular threshold (changes as battle progresses) and any extras are left.  On a PC turn, there is **a 10% chance** that they will use an extra to try and increase damage, if any extras are left.  Looking at damage spells in the core material, considering that area of effect spells would likely hit 2 combatants on average, the average damage was expected to be similar to the per hit damage, so **using an extra will double damage on a hit**.

When determining if an attack hits, a d20 roll is simulated.  **A natural 1 is an automatic miss**, and no damage is done.  **A natural 20 is a critical and always hits**, the total damage, after accounting for the use of an extra, **is doubled**.  This crit rule isn't correct, as it should not double the ability modifier, but this was was easier/quicker to code up and hopefully it doesn't matter on average.

There are many spells used in combat that don't deal damage, these **buffs and debuffs** are not considered.  Such spells can drastically alter the course of an encounter when strategically used and their omission is not a comment on my feelings towards them.  If I can consider a simple way to incorporate them in the future, I will.  Additionally, the concept of **concentration spells is not incorporated** into the simulations.

There are two additional important aspect of D&D encounters which are not built into the simulations.  If an encounter starts to go poorly, PCs can try and run away.  **Fleeing an encounter is not incorporated** into the simulations, for either the PCs or enemies.  Sometimes enemies can be persuaded/intimidated to give up or not fight, or enemies/PCs might offer to surrender if the encounter is going poorly.  **Non-combat solutions are not incorporated** in the simulations.  These solutions often make for an incredibly rich story, and that is what I like about roleplaying games, but that is not the focus of this project.

### The Enemies

There are many possible enemies in D&D, all with different abilities, stats, and other aspects to consider.  Trying to incorporate all of that is beyond the simple approach I have taken.

The _Dungeon Master's Guide_ includes guidelines for creating your own monsters, including ranges of HP, AC, damage per round, etc. which should match up to particular challenge rating (CR) values.  When calculating the difficulty category of an encounter, the CR of each enemy is tied to an amount of XP, and the total XP (along with some other considerations) is how the category is determined.

Instead of going through all possible enemies in the core material, **the monster creation table was used to derive average attributes** for enemies, based on CR.  When an encounter is built, **the average attributes are averaged** to create a single to hit, AC, and damage value used for all enemies.  The **average HP for each CR value is used and the total of these summed** to create a total enemy group HP.

The above choices and treatment of enemies simplifies the simulation but is clearly not indicative of an individual encounter, particularly when there are enemies with vastly different CRs involved.  However, as with other choices outlined above, the assumption is that these inaccuracies should wash out, on average.

While some enemies do have healing abilities, or abilities which make them really hard to actually kill (zombies popping back up to 1 HP every time you knock 'em out, for instance), **enemy healing is not incorporated in the simulations**.

**There are several ways to build an enemy group**.  The user can specify the exact CRs desired, the possible CRs and the number of enemies, the possible CRs and the target difficulty category, the number of enemies and the target difficulty category, or the target difficulty.

In situations where the exact group is not specified, e.g., only the target difficulty is specified, CR values are chosen at random, one at a time, the difficulty calculated, and a decision is made whether or not to stop.  If the difficulty category has been met and the exact number of enemies was not specified, there is a 50/50 chance that enemy group will stop growing.

### Determining Initiative

The initiative order (the order in which combatants take turns) can be determined in several ways.  I decided not to try and assign some average DEX modifier to different combatants and have a series of d20 rolls.  Instead, the **initiative is either determined completely randomly or can be pre-specified**.

Keep in mind that there is no individuality to PCs or enemies, so a PC turn just means the party either heals or tries to do damage to the enemies and an enemy turn means the enemies try to do damage to the party.

The simulated data provided in the repo currently were done with randomly generated initiative orders.  This will not always match real life, particularly when there are more than two or 3 enemies.  DMs will often create enemy groups and roll initiative once for each group.  This can greatly simplify things for the DM and speed up combat.

While the code does not currently include a routine to enforce such an approach, since initiative order can be provided as input, it is possible to do.

### Determing Encounter Outcome

Currently, the encounters are run until one of four conditions are met (some of which are redundant but included to try and cover all bases).  The conditions are evaluated at the end of every combat turn and are: party HP is <= 0, all PCs are 'down', enemy HP is <=0, all enemies are down.

As noted previously, there is currently no mechanism for either PCs or enemies to flee or surrender.  The goal of the project is to gauge how the party might fare on average, and if the encounter looks to be hard the DM will likely be prepared for them to flee or negotiate.  Alternatively, depending on the nature of the enemies, the DM may have rules for when they will try to do the same.  In either case, those considerations are beyond the bounds of the problem.

## Usage

### Python Code

To run a single encounter, the user must first create Party and Enemies BattleGroups.  The default values are set to those described in the previous section.

If the user wants to change the average to hit value, they can provide a value for the ```ATK``` argument.  This can be a single value or a list of values which will be averaged.  For all class arguments, consult the doc strings.

An example which will create a party of 5 first level PCs against a randomly created medium difficulty encounter is given below:

```python
from battle_groups import Party,Enemies
from encounter import Encounter

#use the defaults for the party
party=Party()

#for the enemies, we will only specify medium difficulty
enemies=Enemies(DIFFICULTY='medium')

#create the encounter, initiative randomly determined
encounter=Encounter(party,enemies)

#now run the encounter
encounter.run_encounter()

#look at the results
encounter.summary

```

For both the Enemies object and Encounter object, the user can pass in a random seed via the ```SEED``` argument for reproducibility purposes.  Otherwise, the seed is taken as the system unix timestamp, as an integer.  The ability to set the seed is important when running many simulations in parallel.

Given the assumptions and simplifications I've made, the results of a single encounter simulation are not particularly insightful.  Instead, many simulations should be run and the results looked at in aggregate.  This can be done using configuration files and the ```generate_encounter_results``` function in the _run\_encounters.py_ script.  The _Generate\_CSVs_ python notebook included with the repo provides an example of how to use the code to generate many simulations.  That notebook was used to generate the YAML configuration files and CSV simulated data files included with the repo.

### Included Simulated Data

The repo includes CSV files with simulated data for 10,000 encounters of each of the 4 difficulty categories.  The included _Evaluate\_SimData_ notebook demonstrates reading in the simulated data and some exploration of the results.

A medium blog post summarizing the findings in that notebook is forthcoming.

Plots generated from that notebook are included in the plots directory.  The output scikit-learn trained StandardScaler, PCA, and LogisticRegression objects from the notebook analysis are included in a pickle file in the outputs directory.

## Creative Commons

While I don't intend to profit from this work, the scripts do include some values derived from the D&D main sourcebooks and my assumptions have used the characteristics of source classes, spells, etc., without actively referencing them.  To be safe, I've included the standard creative commons license information.  (If any knows different or spots an issue, please don't hesitate to reach out so I can take corrective measures).

>This work includes material taken from the System Reference Document 5.1 (“SRD 5.1”) by Wizards of
the Coast LLC and available at <https://dnd.wizards.com/resources/systems-reference-document>. The
SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License available at
<https://creativecommons.org/licenses/by/4.0/legalcode>.