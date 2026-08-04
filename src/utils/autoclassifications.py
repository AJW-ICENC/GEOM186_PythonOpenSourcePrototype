"""
Autoclassifications Module

This module contains functions for autoclassifying S-57 ENC data limit Overlaps 
in line with IC-ENC policy


Author: Alex Wallage

v1.0

"""

## import required modules
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import transform
import pyproj
import glog as log
import numpy as np



## Geodesic buffering

def geodesic_buffer(geometry, distance):
    
    """
    Geodesic_buffer: This function uses an Azimuthal projection centred around a geometry to
    create a buffer before reprojecting back to WGS:1984 (Note: all S-57 ENCs should be 
    projected to WGS:1984). This simulates a Geodesic buffer by creating an equal distance projection
    from the centroid of the geometry and buffering in this projection.
    
    To be ran on a geopandas geodataframe geometry using the .apply function for example:
    
    overlap['NameOfGeometry'] = overlap.apply(lambda row: geodesic_buffer(row['GeometryToCreateBuffer'], valOfBuffer))
    
    
    Params
    geometry: (geom) geoDataframe Geometry 
    distance: (int) value of buffer
    
    returns
    buffer_geom_wgs84: buffered geometry on WGS84 projection
    
    """

    try:

        ## validate inputs
        
        if geometry is np.nan:
            return Polygon()
        
        if not isinstance(geometry, (Polygon, MultiPolygon)):
            raise ValueError(f"geometry of {geometry} is not a Polygon or MultiPolygon. It is a {geometry.geom_type}")
        if not isinstance(distance, (int, float)):
            raise ValueError("distance is not an integer or float")

        # log.info(f"Starting geodesic buffer creation for {distance}")
        
        ## Data Analysis 

        #Create a centroid for geometry being buffered
        centroid = geometry.centroid
        x, y = centroid.x, centroid.y
        # log.info(f"Centroid Created")
        
        # Create azimuthal equidistant projection string using centroid
        proj_string = f"+proj=aeqd +ellps=WGS84 +lat_0={y} +lon_0={x} +x_0=0 +y_0=0"
        
        # Define the source and destination CRS
        src_crs = pyproj.CRS("EPSG:4326") # S-57 ENC should be WGS84 - EPSG:4326
        dest_crs = pyproj.CRS(proj_string)
        
        # Create transformers for forward and reverse transformations
        transformer_to_aeqd = pyproj.Transformer.from_crs(src_crs, dest_crs, always_xy=True)
        transformer_to_wgs84 = pyproj.Transformer.from_crs(dest_crs, src_crs, always_xy=True)
        
        # Project to azimuthal equidistant projection
        projected_geom = transform(transformer_to_aeqd.transform, geometry)

        # log.info(f"Geometry Reprojected")

        
        # Create buffer in projected coordinates
        buffer_geom = projected_geom.buffer(distance, cap_style=2) 

        # log.info(f"Buffer Created")

        
        # Transform buffer back to WGS84
        buffer_geom_wgs84 = transform(transformer_to_wgs84.transform, buffer_geom)
        
        # log.info("Geodesic buffer created")

        return buffer_geom_wgs84
    
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": "An unexpected error occurred"}




## Autoclassify overlaps

def autoclassify_overlaps(CWI, overlap):
    
    """
    autoclassify_overlaps: This function takes a geodataframe of ENC data coverage 
    in the IC-ENC standard schema and geodataframe of associated overlaps in the 
    IC-ENC standard schema and autoclassfies the overlaps into 3 categories in line
    with IC-ENC policy D10. 'ACCEPT - 5M', 'ACCEPT - 1M', 'RESIDUAL'. 
    
    It does this by creating geodesic buffers for each buffer size and assessing if 
    the overlap geometries are within the donut buffer
    
    # WORK IN PROGRESS #
    
    
    params
    CWI: (GeodataFrame) all CWIs that are being imported
    overlap: (GeodataFrame) associated overlaps of all CWIs being imported
    
    returns
    classifiedOverlaps: (GeoDataFrame) classifed overlaps of all CWIs being imported
    
    """
     
    try:

        ## Validate inputs

        # validate types
        if not isinstance(CWI, gpd.GeoDataFrame):
            raise ValueError(f"geometry of {CWI} is not a Polygon or MultiPolygon. It is a {CWI.geom_type}")
        
        if not isinstance(overlap, gpd.GeoDataFrame):
            raise ValueError(f"geometry of {overlap} is not a Polygon or MultiPolygon. It is a {overlap.geom_type}")
        

        # Validate data structure
        cwiReqCols = ['CELLNAME', 'geometry'] # only columns used in analysis
        for col in cwiReqCols:
            if col not in CWI.columns:
                raise ValueError(f"missing required column: {col}")
            
        overlapReqCols = ['CELLNAME_1', 'STATUS','geometry']
        for col in overlapReqCols:
                if col not in overlap.columns:
                    raise ValueError(f"missing required column: {col}")
        

        # Check for missing values
        if CWI[cwiReqCols].isnull().any().any():
            raise ValueError("Missing values found in critical columns")
        
        if overlap[overlapReqCols].isnull().any().any():
            raise ValueError("Missing values found in critical columns")


        # Invalid Geometry check
        if not CWI.geometry.is_valid.all():
            raise ValueError("Invalid geometries found in the GeoDataFrame")
        
        if not overlap.geometry.is_valid.all():
            raise ValueError("Invalid geometries found in the GeoDataFrame")



        ## Data Engineering
        
        # define CWI information for join
        CWI = CWI[['CELLNAME', 'geometry']]
        
        # assign uniques ids
        overlap = overlap.assign(unique_id=range(1, len(overlap) + 1))
        
        # rename fields for join
        overlap = overlap.rename(columns={'geometry': 'geometryOverlap'})
        CWI = CWI.rename(columns={'geometry': 'geometryCWI'})
        
        # join overlaps and CWI gdb based on CELLNAME
        overlap = overlap.merge(CWI, left_on='CELLNAME_1', right_on="CELLNAME", how='left')
        overlap = overlap.drop_duplicates(subset=['unique_id']) # CONFIRM IF THIS REQUIRED
        
        # Set the geometry to geometryOverlap for CRS check and buffering
        overlap = overlap.set_geometry('geometryOverlap')
        
        # Ensure the CRS is in a geographic coordinate system for geodesic buffering
        if not overlap.crs.is_geographic:
            overlap['geometryOverlap'] = overlap['geometryOverlap'].to_crs(epsg=4326)
            overlap['geometryCWI'] = overlap['geometryCWI'].to_crs(epsg=4326)
        


        ## Create geodesic buffers
        
        # Assign values for buffers
        distances = [-5, -1, -0.1]
        # loop through and create donut buffer for each buffer distance
        for distance in distances:
            
            # define geometry attribute name
            buffer_name = f'buffer_{abs(distance)}m'
            
            # create buffer geometry
            overlap[buffer_name] = overlap.apply(lambda row: geodesic_buffer(row['geometryCWI'], 0.1).difference(geodesic_buffer(row['geometryCWI'], distance)), axis=1)
        
        
        
        ## Autoclassify Overlaps
        
        # Check if geometryOverlap is within each of the buffers and update STATUS field accordingly
        def update_status(row):
            
            if row['geometryOverlap'].within(row['buffer_0.1m']):
                return 'RESIDUAL'
            
            elif row['geometryOverlap'].within(row['buffer_1m']): # ADD CHECK FOR DIFF PRODUCERS
                return '1mOverlap'
            
            elif row['geometryOverlap'].within(row['buffer_5m']):
                return '5mOverlap'
            
            else:
                return 'FOR REVIEW'
            
        overlap['STATUS'] = overlap.apply(update_status, axis=1)


        ## reformat Overlaps Gdb inline with overlap schema

        overlap = overlap.rename(columns={'geometryOverlap': 'geometry'})

        classifiedOverlaps = gpd.GeoDataFrame(overlap[['DMD_ID_1', 'CELLNAME_1', 'ED_NO_1', 'NAV_BAND_1', 'SCALE_1',
            'MODIFIC_1', 'DMD_ID_2', 'CELLNAME_2', 'NAV_BAND_2', 'ED_NO_2', 'SCALE_2', 'MODIFIC_2',
            'geometry', 'STATUS', 'NAMEJOIN', 'OVERLAP_ID']], geometry='geometry') # maybe include unique id?

        return classifiedOverlaps
    
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": "An unexpected error occurred"}


# end of script