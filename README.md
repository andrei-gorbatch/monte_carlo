# Combat encounters in DnD using Monte-Carlo method
* This is a small project based on Monte-Carlo method.
* The aim is to provide an easy way to test combat encounters in DnD 5e.
* To see app deployment online, check https://dnd-combat-simulator.nw.r.appspot.com/

# How to run this repository in python
* Install required environment from requirements.txt
* Upload Excel file with information about your heroes and monsters to data/upload_xlsx_here/character_info.xlsx. You can find a sample file in data/sample.
* Run simulation.py. Statistics about your combat will be published in terminal. More detailed information is stored in data/simulation.

# Scripts
1. main.py - script that provides app frontend. 
2. Simulation.py - script that runs the combat simulation based on information from data/upload_xlsx_here/character_info.xlsx (or from uploaded through web app)
3. Classes.py - definitions of python classes for characters. Currently two distinct classes are supported: "martial (hit with a stick)" and "blaster (hit with a fireball)"
4. utils.py - small useful functions
5. config.py - parameters of the simulation, such as number of iterations.
6. run_tests.py - run all tests in tests/ folder
