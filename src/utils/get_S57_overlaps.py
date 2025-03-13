
"""
S-57 ENC overlaps module

This module contains functions to create and filter 
S-57 ENC overlaps geodataframes

List of functions:
    check_overlaps()
    filter_policy()


Author: AJW

last amended: AJW 03/02/2025

date: 03/02/2025

v1.0

"""

## import packages

import geopandas as gpd
import glog as log

 

    
## filter policy

def filter_policy(gdf):
    
    """
    filter_policy: This function filters a geodataframe of S-57 ENC
    overlaps in accordance with IC-ENC Policy D10  
    the input must be in the standard format as outlined in...
    
    params
    gdf:
    
    returns
    gdf:
    
    """

    try:

        ## Validate inputs

        # check types
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise ValueError("gdf must be a GeoDataFrame")
        
        # check data structure
        reqCols = ['CELLNAME_1', 'CELLNAME_2', 'NAV_BAND_1', 'NAV_BAND_2', 'SCALE_1', 'SCALE_2']
        for col in reqCols:
            if col not in gdf.columns:
                raise ValueError(f"missing required column: {col}")
        


        ## Data Analysis 

        log.info("Starting filter policy check")

        # filter gdf
        gdf = gdf[
            (gdf['NAV_BAND_1'].astype(int) == gdf['NAV_BAND_2'].astype(int)) | 
            (gdf['SCALE_1'].astype(int) == gdf['SCALE_2'].astype(int))
        ]

        gdf = gdf[gdf['CELLNAME_1'] != gdf['CELLNAME_2']]

        log.info("Overlaps filtered successfully")

        return gdf
    
    except ValueError as ve:
        log.error(f"ValueError: {ve}")
        return {"status": "error", "message": str(ve)}
    
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": "An unexpected error occurred"}



def overlap_engineering(gdf):
    """


    """


    # check and amend fields
    
    reqCols = ["DMD_ID_1", "CELLNAME_1", "SCALE_1", "NAV_BAND_1", "MODIFIC_1", "ED_NO_1", "DMD_ID_2", "CELLNAME_2", "SCALE_2", "NAV_BAND_2", "MODIFIC_2", "ED_NO_2", "STATUS",  "geometry", "NAMEJOIN", "OVERLAP_ID"]
    
    drCols = ["DMD_ID", "CELLNAME", "SCALE", "NAVBAND", "MODIFIC", "ED_NO"]
    
    for col in gdf.columns:
        if col not in reqCols[0:-2]: # remove NAMEJOIN and OVERLAP_ID

            # check if col hasn't had number assigned
            if col in drCols:
                gdf = gdf.rename(columns={col: f"{col}_1"})
                log.info(f"{col} renamed to {col}_1")
            else:
                log.info(f"dropping column: {col}")
                gdf = gdf.drop(col, axis=1)
    


    #add additonal fields

    if "STATUS" not in gdf.columns:
        gdf["STATUS"] = "FOR_REVIEW"

    if "NAMEJOIN" not in gdf.columns:
        gdf["NAMEJOIN"] = gdf["CELLNAME_1"].astype(str) + gdf["CELLNAME_2"].astype(str)

    if "OVERLAP_ID" not in gdf.columns:
        gdf["OVERLAP_ID"] = gdf["CELLNAME_1"].astype(str) + gdf["ED_NO_1"].astype(str) + gdf["CELLNAME_2"].astype(str) + gdf["ED_NO_2"].astype(str)


    for col in reqCols:
        if col not in gdf.columns:
            gdf[col] = ""
            log.info(f"Column {col} missing from overlaps geodataframe, please note this will be empty in the database")
    
    
    return gdf

## Check Overlaps

def check_overlaps(gdf1, gdf2, ov_type="DR"):
    
    """
    check_overlaps: This function creates overlaps between two geodatabases
    and returns a geodatabase of the overlap extents with the attribution of both intact

    params
    gdf1: (geodataframe) to be overlayed
    gdf2: (geodataframe) to be overlayed with
    ov_type: (string) key word passed depending on type of overlap check 
        (potential options: 'DR' : data reg, 'EX' : exchange set, 'CU' : Catalogue update)
    
    returns
    overlaps: (geodataframe) overlapping geometries or error message
    """
    
    try:
        ## Validate inputs

        # check types
        if not isinstance(gdf1, gpd.GeoDataFrame):
            raise ValueError("gdf1 must be a GeoDataFrame")
        if not isinstance(gdf2, gpd.GeoDataFrame):
            raise ValueError("gdf2 must be a GeoDataFrame")
        if not isinstance(ov_type, str):
            raise ValueError("ov_type must be a string")
        if ov_type not in ["DR", "EX", "CU"]:
            raise ValueError("ov_type must contain a value from ['DR', 'EX', 'CU']")
        
        # check data structure

        # check missing values
        


        ## Data Analysis

        log.info("Starting overlap check")
        
        # Check for overlaps
        gdf = gpd.overlay(gdf1, gdf2, how='intersection')



        ## Data Engineering

        if ov_type == "DR":
            gdf = overlap_engineering(gdf)
        elif ov_type == "EX":
            # may need different data engineering for Exchnage set, remove logic if not
            pass
        else:
            # may need different data engineering for Catalogue update, remove logic if not
            pass
        
        log.info("Overlap check completed successfully")
        
        return gdf
    
    except ValueError as ve:
        log.error(f"ValueError: {ve}")
        return {"status": "error", "message": str(ve)}
    
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": "An unexpected error occurred"}



## merge overlap gdbs
 
def merge_overlaps(*args):
    for x in args:
        pass
    pass



# end of script