"""
Author: Camilo Toruno
Function used to aggregate EnergyPlus pipeline simulation results
"""

from pathlib import Path
import os 
import pandas as pd
import csv
import tqdm 
import tempfile
import time

class Job:
    """
    Represents a custom object with folder, schedule, and xml attributes.
    """
    def __init__(self, eplusout, weather_scenario, city, bldg, year):
        # require initialization with the folder of the files for the building
        self.weather_scenario = os.path.basename(weather_scenario)  
        self.city = os.path.basename(city)
        self.bldg = bldg
        self.year = int(os.path.basename(year).split(self.city.replace(' ', '.'))[1].split(self.weather_scenario)[0].strip('_'))  
        self.bldg_id = int(os.path.basename(bldg).split('bldg')[1].lstrip('0'))  # # (l)strip the (preceding) zeros off a bldg number (e.g. bldg000123 -> 123)
        self.eplusout = eplusout

        # values to be updated
        self.batch_id = None 


def create_jobs(**arguments):
    jobs = []
    # Get all folders in the current directory
    for scenario in Path(arguments.get('simulation_res_fldr')).glob("*"):
        for city in Path(scenario).glob("*"):
            for bldg in Path(city).glob("*"):
                for year in Path(bldg).glob("*"):
                    eplusout = year / 'eplusout.csv'
                    if eplusout.exists():
                        jobs.append(Job(eplusout, scenario, city, bldg, year))

    return jobs 


def aggregate_results(job, arguments):
    options = arguments.get("options")

    # Split the column "Date/Time" string values with " " and create a new column "Date" with first element of split 
    eplusout = pd.read_csv(job.eplusout)

    ### If the Date/Time column is the Day/Month/Year, split into components 
    # eplusout['Date'] = eplusout['Date/Time'].str.split().str[0]
    # eplusout[['Month', 'Day']] = eplusout['Date'].str.split('/', expand=True)
    # eplusout = eplusout.drop('Date/Time', axis=1)        # Delete the "Date/Time" column 

    ### If date/time column is just the month, rename to Month
    eplusout = eplusout.rename(columns={'Date/Time': 'Month'})

    aggregated_results = pd.DataFrame(columns= eplusout.columns)

    # aggregate results by month 
    for i, month in enumerate(eplusout["Month"].unique()):
        # set the date range
        date_rows = eplusout["Month"] == month
        aggregated_results.loc[i, "Month"] = month
        aggregated_results.loc[i, 'bldg_id'] = int(job.bldg_id)
        aggregated_results.loc[i, "Year"] = job.year
        aggregated_results.loc[i, "Weather Scenario"] = job.weather_scenario

        # for the columns to average, avereage results
        for column_name in options.get("columns_to_average"):
            aggregated_results.loc[i, column_name] = eplusout.loc[date_rows, column_name].mean()
            aggregated_results.loc[i, column_name] = aggregated_results.loc[i, column_name].astype(float)

        # for the remaining columns sum their values
        for column_name in eplusout.columns:
            if (column_name not in options.get("columns_to_average")) and (column_name not in options.get("unchanged_columns")):
                aggregated_results.loc[i, column_name] = eplusout.loc[date_rows, column_name].sum()
                aggregated_results.loc[i, column_name] = aggregated_results.loc[i, column_name].astype(float)

    return aggregated_results


def _load_header(results_file):
    # load header 
    with open(results_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        return header 


def _add_columns(new_header, results_file, new_columns):

    with tempfile.TemporaryFile(mode='w+', newline='') as temp_file:  # Create temporary file
        with open(results_file, 'r') as f:  # Open original file for reading
            reader = pd.read_csv(f, chunksize=2000) 
            writer = csv.writer(temp_file)
            writer.writerow(new_header) 

            for chunk in reader:    # for chunks of 2000 file lines to limit memory usage 

                for col in new_columns: chunk[col] = None   # set the new columns in the chunk of the file to none
                chunk = chunk.fillna("")                    # Set missing values to empty string 

                writer.writerows(chunk.to_records(index=False))  # Write to temporary file

        # Overwrite original file with temporary file contents
        with open(results_file, 'w') as f:
            temp_file.seek(0)           # Rewind temporary file to beginning
            f.write(temp_file.read())   # Copy contents


def write_data(outputdata, results_file):

    if not results_file.exists(): 
        outputdata.to_csv(results_file, index=False)

    else:
        header = _load_header(results_file)
        new_columns = set(outputdata.columns) - set(header)                     # Id new columns for header
        outputdata_missing_cols = set(header) - set(outputdata.columns)         # Identify missing columns in outputdata
        header.extend(new_columns)                                              # add new columns to header

        for col in outputdata_missing_cols: 
            outputdata[col] = None                  # Add missing columns to outputdata with None values (empty cells)

        outputdata = outputdata[header]             # Sort outputdata columns by the order in results

        # if there's new columns then add columns to existing results
        if new_columns: _add_columns(header, results_file, new_columns)
            
        # Append outputdata to updated results_file
        with open(results_file, 'a') as f: 
            outputdata.to_csv(f, header=False, index=False)
        

def run(arguments):
    """
        create a summary results data
        for job in jobs:
            # try to open the simulation results folder 

            # join pricing data on table

            # calculate cost per time period

            # aggregate to aggregated_time_period to make summary
                for each column aggregate properly 
                    - keep first index's value
                    - sum 
                    - average
                    
            # join new summary data on metadata file 

            if there's new columns in eplusout.columns that aren't in results_columns
            add new columns from eplusout.columns to the end of the columns in results
            initialize the new cells of the new columns as empty for the existing rows in results

            # vertical concatenate the total summary data with new summary data
    """

    arguments["results_file"] = Path(arguments.get('simulation_res_fldr')).joinpath(arguments.get('options').get('results_file'))

    if arguments.get('results_file').exists():
        if arguments.get("overwrite"):
            print(f"Deleteing output file: {arguments.get('results_file')}. Cancel job now if overwrite chosen in error.")
            time.sleep(10)
            os.remove(arguments.get('results_file'))

        else: 
            print(f"Output file exists: {arguments.get('results_file')}. \nOverwrite set to false. Data will be appended to output file")
            time.sleep(10)

    jobs = create_jobs(**arguments)

    for job in tqdm.tqdm(jobs, total=len(jobs), desc="Processing files", smoothing=0.01):
        outputdata = aggregate_results(job, arguments)
        write_data(outputdata, results_file = arguments.get('results_file'))