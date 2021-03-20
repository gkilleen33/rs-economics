# -*- coding: utf-8 -*-

import ee 

ee.Initialize()

###############################################################
# ENTER USER INPUTS HERE  
###############################################################
plot_boundaries = ee.FeatureCollection() # Upload plot boundary data (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes

# Export information (to Google Drive)
output_folder = 'EXAMPLE_FOLDER'  # Folder name to save outputs in Google drive. The folder should be created before running the script.
output_file = 'EXAMPLE_FILE_NAME' # Output file name  

##############################################################
# END USER INPUTS 
##############################################################

#Construct AOI
aoi = plot_boundaries.geometry().bounds()

# Import elevation data 
elevation = ee.Image('USGS/SRTMGL1_003').select('elevation').clip(aoi)

# Store the native resolution of the SRTM data 
srtm_scale = elevation.projection().nominalScale().getInfo()

# Calculate slope and aspect 
terrain = ee.Terrain.products(elevation)

# If the scale of the smallest item in 'plot_boundaries' is less than the native resolution of the GPM data, then set the variable scale to the min scale of polygons, otherwise set it to the native resolution
def addArea(feature):
    return feature.set({'area': feature.geometry().area()})  
polygons_with_area = plot_boundaries.map(addArea)

min_polygon_area = polygons_with_area.reduceColumns(reducer=ee.Reducer.min(), selectors=['area']).getInfo()['min']

if min_polygon_area < (gpm_scale)**2:
    scale = max(10, math.sqrt(min_polygon_area)) # In case there are any polygons with very small area 
else: 
    scale = gpm_scale

# Calculate zonal stats 
zonal_stats = terrain.reduceRegions(reducer=ee.Reducer.mean(), collection=plot_boundaries, scale=scale, tileScale=4)

# Remove geometry 
def removeGeometry(feature):
    return feature.setGeometry(None)

zonal_stats_no_geometry = zonal_stats.map(removeGeometry)

# Export the data to Google Drive
task = ee.batch.Export.table.toDrive(collection=zonal_stats_no_geometry, description=output_file, 
                        fileFormat='CSV', fileNamePrefix=output_file,
                        folder=output_folder)

task.start()    
