# -*- coding: utf-8 -*-

import ee 

ee.Initialize()

###############################################################
# ENTER USER INPUTS HERE  
###############################################################
plot_boundaries = ee.FeatureCollection() # Upload plot boundary data (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes

# Start and end dates for image search (YYYY-MM-DD)
begin = ee.Date() # E.g. '2019-08-01'
end = ee.Date() # E.g. '2019-12-15'

# Export information (to Google Drive)
output_folder = 'EXAMPLE_FOLDER'  # Folder name to save outputs in Google drive. The folder should be created before running the script.
output_file = 'EXAMPLE_FILE_NAME' # Output file name  

##############################################################
# END USER INPUTS 
##############################################################

#Construct AOI
aoi = plot_boundaries.geometry().bounds()

# Import GPM rainfall data and SRTM elevation data 
gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_V06').filter(ee.Filter.date(begin, end))\
    .filterMetadata('status', 'equals', 'permanent')

# Store the native scale of the GPM data in a variable to later pass to zonal stats
gpm_scale = gpm.first().select('precipitationCal').projection().nominalScale().getInfo()

# Create a separate image collection by day
number_of_days = end.difference(begin, 'day')
def calculateDays(day):
    return begin.advance(day,'day')

list_of_days = ee.List.sequence(0, number_of_days.subtract(1)).map(calculateDays)

# Calculate average rainfall for each day (mm/hr)
def averageDailyRainfall(date, newlist):
	# Cast values
    date = ee.Date(date)
    newlist = ee.List(newlist)
    
    # Filter collection between date and the next day
    filtered_day = gpm.filterDate(date, date.advance(1,'day'))
    image = filtered_day.mean().select('precipitationCal').clip(aoi).set({'Date': date}).rename('average_rainfall')

    # Add the mosaic to a list only if the collection has images
    return ee.List(ee.Algorithms.If(filtered_day.size(), newlist.add(image), newlist))

rain_by_day = ee.ImageCollection(ee.List(list_of_days.iterate(averageDailyRainfall, ee.List([]))))

# If the scale of the smallest item in 'plot_boundaries' is less than the native resolution of the GPM data, then set the variable scale to the min scale of polygons, otherwise set it to the native resolution
def addArea(feature):
    return feature.set({'area': feature.geometry().area()})  
polygons_with_area = plot_boundaries.map(addArea)

min_polygon_area = polygons_with_area.reduceColumns(reducer=ee.Reducer.min(), selectors=['area']).getInfo()['min']

if min_polygon_area < (gpm_scale)**2:
    scale = max(10, math.sqrt(min_polygon_area)) # In case there are any polygons with very small area 
else: 
    scale = gpm_scale

# Calculate rainfall for each plot and day
# Note: for GPM we have to specify a scale below the native resolution because pixel sizes are much larger than plot size
# Nearest neighbor resampling (the default) is used, so there is no transformation to the data
def zonalStats(image):
    date = image.get("Date")
    toReturn = image.reduceRegions(reducer=ee.Reducer.mean(), collection=plot_boundaries, scale=scale, tileScale=4)
    return toReturn.set('Date', date)

zonal_stats = rain_by_day.map(zonalStats)

#  Remove geometry from the zonal stats
def processFeature(feature):
    return feature.setGeometry(None)

def removeGeometry(featureCollection):
    fc = ee.FeatureCollection(featureCollection)  # Cast
    fc_date = ee.Date(fc.get('Date')).format('yyyy-MM-dd')  # Get date to assign
    fc_no_geometry = fc.map(processFeature)
    toReturn = fc_no_geometry.map(lambda x: x.set({'Date': fc_date}))
    return toReturn

zonal_stats_no_geometry = zonal_stats.map(removeGeometry).flatten()

# Export the data to Google Drive
task = ee.batch.Export.table.toDrive(collection=zonal_stats_no_geometry, description=output_file, 
                        fileFormat='CSV', fileNamePrefix=output_file,
                        folder=output_folder)

task.start()    
