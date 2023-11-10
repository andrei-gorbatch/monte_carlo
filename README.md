# Combat encounters in DnD using Monte-Carlo method
* This is a small project based on Monte-Carlo method.
* The aim is to provide an easy way to test combat encounters in DnD 5e.
* The repository aims to ingest data on players and monsters and provide an estimation of how the combat encounter will go.

# How to run this repository
* Install required environment in Conda
* Upload Excel file with information about your heroes and monsters to data/upload_xlsx_here/character_info.xlsx. You can find a sample file in data/sample.
* Run src/simulation.py. Statistics about your combat will be published in terminal. More detailed information is stored in data/simulation.

# Directory structure:
* environment/ - environment information
* src/ - all python scripts
* notebooks/ - Jyputer notebooks for testing
* data/ - where all data is stored

# Scripts
1. Simulation.py - main script that runs the combat simulation based on information from data/upload_xlsx_here/character_info.xlsx
2. Classes.py - definitions of python classes for characters. Currently two distinct classes are supported: "martial (hit with a stick)" and "blaster (hit with a fireball)"
3. utils.py - small useful functions
4. config.py - parameters of the simulation, such as number of iterations.
