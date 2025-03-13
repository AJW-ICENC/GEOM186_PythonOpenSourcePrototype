"""
IC-ENC gaps and overlaps analysis - Potential Overlaps creation and classification test

This script tests a workflow for creating and autoclassifying potential
overlaps for S-57 ENC data limits. It compares incoming ENC data limits 
against All Open CWIS in the IC-ENC validation workflow and against all
ENC data limits currently on the market. 

When IC-ENC move to a SQL gdb approach for gaps and overlaps data structure, the inputs will
need to be changed to SQL queries to extract the required data. Geopandas can handle SQL as 
an input but this needs to be tested as it may impact scripts later down the line. 


Author: Alex Wallage

last amended: AJW 18/02/2025

date: 03/02/2025

v1.0

"""



## enable venv before testing begins

import subprocess
import sys
import os

def activate_venv():
    # Get working dir
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct relative path to venv
    venv_path = os.path.join(current_dir, '..', '..', 'venv')

    # create activate venv command
    activate_command = os.path.join(venv_path, 'Scripts', 'activate')

    # run venv
    subprocess.run(activate_command, shell=True, check=True)

    # List packages in  venv
    venv_packages = subprocess.run(['pip', 'list'], capture_output=True, text=True).stdout

    # List global packages
    global_packages = subprocess.run(['pip', 'list', '--user'], capture_output=True, text=True).stdout

    # check if venv is active
    if venv_packages == global_packages:
        print("Error: Virtual environment is not activated.")
        sys.exit(1)

activate_venv()



## Add src module to python paths 

def activate_module():

    # check if package is already available
    if os.path.abspath(os.path.join(os.path.dirname(__file__) , "../../src")) not in sys.path:
        print(" utils not in sys path, adding now") # somewhat hacky - is there a better approach?

        # add package to file paths
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__) , "../../src")))

activate_module()



## import modules

import pandas as pd
import geopandas as gpd
from tkinter import filedialog # just for testing
import glog as log

import utils



## define main process flowline
def main():

    # get input path (DAILY INPUT) - read into gdf
    file_path = filedialog.askopenfilename()

    df1 = gpd.read_file(file_path)

    name = file_path.split("\\")[-1]

    log.info(f"Starting Overlap assessment on: {name}")


    ## define Open CWIs and ALLRELEASED data locations - update when we move to SQL db
    file_path1 = "V:\\MANAGEMENT\\IC-ENC Graphical Catalogue\\In work\\Model View Layers\\ALLRELEASED.shp" # Will be LIVE GDB

    file_path2 = "V:\\MANAGEMENT\\IC-ENC Graphical Catalogue\\In work\\Model View Layers\\WEEKLY_CELLS (PROJECT).shp" # WILL BE CWI GDB (OPEN) filtered

    file_path3 = "V:\\MANAGEMENT\\IC-ENC Graphical Catalogue\\In work\\Model View Layers\\IC-ENC_NON_RELEASED (PROJECT).shp" # WILL BE CWI GDB (OPEN) filtered
    
    file_paths = [file_path1, file_path2, file_path3]


    # initalise gdf to store outputs
    overlapsGdf = gpd.GeoDataFrame()

    # iterate through each path
    for path in file_paths:

        name = path.split("\\")[-1]

        log.info(f"Assessing against {name}")

        # read in df
        df2 = gpd.read_file(path)

        # create overlaps
        gdf = utils.check_overlaps(df1, df2) # process return errors?

        # remove overlaps that are not inline with IC-ENC policy D10 - not same nav band or scale
        gdf = utils.filter_policy(gdf) # process return errors?

        # only autoclassify if overlaps have been created.
        if not gdf.empty:

            # autoclassify overlaps for 5m, 1m, residual
            gdf = utils.autoclassify_overlaps(df1, gdf)

            # amend to the output gdf
            overlapsGdf = pd.concat([overlapsGdf, gdf], ignore_index=True)
        
        log.info(f"Overlaps for {name} have been generated and autoclassified")

    # save output file.
    overlapsGdf.to_file("G:\\IC-ENC USERS\Alex Wallage\\Gaps and Overlaps Diss\\TrialData\\TestData05022025\\newModelOutput\\overlapsTest.shp")

    log.info("Process finsished")



## initialise main funcion when file is ran directly
if __name__ == "__main__":
    main()


## Disable venv
deactivate_command = "deactivate"
subprocess.run(deactivate_command, shell=True, check=True)


# end of script