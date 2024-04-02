import eprun_s
import multiprocessing
import os 
import sys

if __name__ == '__main__':
    multiprocessing.freeze_support()        # required to prevent issues for multicore processing in run_energyplus_simulations() 

    arguments = {
        'cities': ['Detroit', 'Los Angeles'], 
        # 'cities': ['Dallas', 'Philadelphia'],
        'climate_scenarios': ["historical_1980-2020", "rcp45cooler_2020-2060"],
        }

    run_args = {

        'weather_folder': '/Volumes/seas-mtcraig/EPWFromTGW/TGWEPWs',
        # 'weather_folder': '/Users/camilotoruno/Documents/GitHub/EnergyPlus-Python/TGWEPWs_trimmed',

        'buildings_folder': "/Users/camilotoruno/Documents/local_research_data/buildings_LA_Detroit",

        'output_folder': '/Users/camilotoruno/Documents/local_research_data/simulations_LA_Detroit',
        # 'output_folder': 'Volumes/seas-mtcraig/ctoruno/Buildings_Dallas_downsample_simulations',
        # 'output_folder': '/Users/camilotoruno/Documents/GitHub/EnergyPlus-Python/simulations',

        'overwrite_output': True, 
        'verbose': False,
        "max_cpu_load": 0.7,       # must be in the range [0, 1]. The value 1 indidcates all CPU cores, 0 indicates 1 CPU core

        'ep_install_path': '/Applications/OpenStudio-3.4.0/EnergyPlus',


        # Optional - Define the desired simulation settings. These can be set during the IDF generation 
        # or prior to simulation. 
        ############  required if setting IDF file requested outputs here rather than in upstream 
        # 'ResStockToEnergyPlus_repository': '/Users/camilotoruno/Documents/GitHub/building_energy_modeling',         
        # 'pathnameto_eppy': "/Users/camilotoruno/anaconda3/envs/research/lib/python3.11/site-packages/eppy",
        # "iddfile": "/Applications/OpenStudio-3.4.0/EnergyPlus/Energy+.idd",
        # 'idf_configuration': "/Users/camilotoruno/Documents/GitHub/EnergyPlus-Python/simulation_output_configuration.idf",      # output settings configuration
        ###########
        }


    ################################## RUN SMULATIONS ############################################

    sim = 1
    total_sims = len(arguments['climate_scenarios']) * len(arguments['cities'])
    for scenario in arguments['climate_scenarios']:
        for city in arguments['cities']:
            print(f"========================== Run \t City \t\t\t Scenario ==========================")
            print(f"========================== {sim}/{total_sims} \t {city} \t\t {scenario} ==========================")
            run_args['city'] = city
            run_args['climate'] = scenario
                # Generate list of simulation jobs to run 
            jobs = eprun_s.generate_simulation_jobs(**run_args)

            # if the user specified energy plus simulation outputs, ensure they're set within the IDF file
            if "idf_configuration" in run_args.keys():
                bldg_to_idf_repository = run_args['ResStockToEnergyPlus_repository']
                if os.path.exists(bldg_to_idf_repository): sys.path.append(bldg_to_idf_repository)            # Source custom script
                else: raise RuntimeError(f'Cannot find ResStockToEnergyPlus repository for setting IDF simulation outputs {bldg_to_idf_repository}')

                import functions      # import once the path is added 
                for job in jobs: job.idf = job.idf_path  # make compatible with upstream workflow function 
                functions.reset_idf_schedules_path.set_EnergyPlus_Simulation_Output(jobs, **run_args)

            eprun_s.run_energyplus_simulations(jobs, **run_args)
            sim += 1
            print("\n\n")
