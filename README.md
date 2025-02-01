# EnergyPlus Python Simulation Pipeline

# Prior EnergyPlus Development History
See development commit history of this repostiory branch in the repository building_energy_modeling
[here](https://github.com/camilotoruno/EnergyPlus-Python).

# Description of scripts and usage
## Simulation
### script_epwork.py Setup:
This is the main workflow script. Use it to run a large job for building energy simulations. Define the parameters of the simulation in the file (e.g. list of cities and climate scenarios to run the simulation for). Then run the program either from an IDE or terminal. 

### eprun_s.py Example usage: 
This is the core functionality which is orchestrated by script_epwork.py. There's no need to directly call it, however it can be called directly from the command line. 

## Results Pre-Proceesing
### run_output_aggregation.py
Use script to aggregate output from simulation results folder. This is currently set up for to monthly data, however you may need to change the data to aggregate truly monthly data. Changing the reporting frequency changes the column header changes (e.g. Date/Time, Date), and thus this script will need to be modified lighly for different frequencies. Keep in mind the design of the aggregation script to read and write single lines (rather than loading the full output file) to avoid loading the entire aggregated csv in memory (because it could be larger than memory for large building simulation files). 

### ep_res_aggregation.py
Function used by **run_output_aggregation.py** to aggregate the simulation outputs from EnergyPlus (in the output folders of the structure [text](<simulations/historical_1980-2020/Albuquerque/bldg0000772/bldg0000772_Albuquerque_1980_historical_1980-2020/eplusmtr.csv>))

## Climate Change Warming Signals
### CONUS_global_warming_deltas_aggregation.ipynb
Use to aggregate the global and national warming signals for each year to label simulation data 

### conus_and_global_warming_plotting.R
Use to plot CONUS / Global warming signals by each other and time

## Energy Pricing
### pricing_data_cleaning.ipynb
Use this to clean up EIA / FRED electriicty, natural gas, etc pricing data and format it for the next step, calculating household costs. Manually pre-processed EIA data is held in ```seas-mtcraig/data_sharing/Energy Burdens Under Climate Change/Energy rates```

## Analysis
### joining_metadata_calculating_costs.ipynb
Use to join the metadata (buildstock.csv) data on the aggregated results, calculate household level costs. 

### dataManipulation_analysis_and_plotting.ipynb
Use this to plot maps of the EnergyBurden across the US, and process data to annual and seasonal metrics. Determine the change in key energy metrics by percentiles (e.g. 50th percentile energy burdens per each household per city)
