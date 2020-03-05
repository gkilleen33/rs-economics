# -*- coding: utf-8 -*-

import ee 

ee.Initialize()

###############################################################
# ENTER USER INPUTS HERE  
###############################################################
plot_boundaries = ee.FeatureCollection() # Upload plot boundary data (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes
aoi = ee.FeatureCollection() # Upload AOI polygon (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes
# The AOI can contain multiple polygons, but should be relatively simple. A bounding box or convex hull around all plot boundaries is appropriate

# Export information (to Google Drive)
output_folder = 'EXAMPLE_FOLDER'  # Folder name to save outputs in Google drive. The folder should be created before running the script.
output_file = 'EXAMPLE_FILE_NAME' # Output file name  

##############################################################
# END USER INPUTS 
##############################################################

# Import elevation data 
elevation = ee.Image('USGS/SRTMGL1_003').select('elevation').clip(aoi)

# Store the native resolution of the SRTM data 
srtm_scale = elevation.projection().nominalScale().getInfo()

# Calculate slope and aspect 
terrain = ee.Terrain.products(elevation)

# Caclulate zonal stats 
zonal_stats = terrain.reduceRegions(reducer=ee.Reducer.mean(), collection=plot_boundaries, scale=srtm_scale)

# Remove geometry 
def removeGeometry(feature):
    return feature.setGeometry(None)

zonal_stats_no_geometry = zonal_stats.map(removeGeometry)

# Export the data to Google Drive
task = ee.batch.Export.table.toDrive(collection=zonal_stats_no_geometry, description=output_file, 
                        fileFormat='CSV', fileNamePrefix=output_file,
                        folder=output_folder)

task.start()    
