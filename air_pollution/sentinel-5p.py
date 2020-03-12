# -*- coding: utf-8 -*-

import ee 
import math 

ee.Initialize()

###############################################################
# ENTER USER INPUTS HERE  
###############################################################
polygons = ee.FeatureCollection() # Upload boundary data for the areas of interest (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes

# Start and end dates for image search (YYYY-MM-DD)
begin = ee.Date() # E.g. '2019-08-01'
end = ee.Date() # E.g. '2019-12-15'

# Pollution types. Options are 'UV' (UV aerosol index), 'CO' (carbon monoxide), 'CH2O' (formaldehyde), 'NO2' (nitrogen dioxide), 'O3' (ozone), 'SO2' (sulphur dioxide), and 'CH4' (methane)
# All air quality metrics should be included in a list, e.g. ['UV', 'CO'] for UV and CO, or ['UV'] for just 'UV'
pollution_types = ['UV', 'CO']

# Export information (to Google Drive)
output_folder = 'EXAMPLE_FOLDER'  # Folder name to save outputs in Google drive. The folder should be created before running the script.
output_file = 'EXAMPLE_FILE_NAME' # Output file name  

##############################################################
# END USER INPUTS 
##############################################################

#Construct AOI
aoi = polygons.geometry().bounds()

# Extract selected pollution types

if len(pollution_types) < 1:
    raise Exception('At least one pollution type must be selected')

if 'UV' in pollution_types:
    UV = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI')\
    .select('absorbing_aerosol_index')\
    .filterDate(begin, end).filterBounds(aoi)

if 'CO' in pollution_types:
    CO = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_CO')\
    .select('CO_column_number_density')\
    .filterDate(begin, end).filterBounds(aoi)

if 'CH2O' in pollution_types:
    CH2O = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_HCHO')\
    .select('tropospheric_HCHO_column_number_density')\
    .filterDate(begin, end).filterBounds(aoi)

if 'NO2' in pollution_types:
    NO2 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2')\
    .select(['NO2_column_number_density', 'tropospheric_NO2_column_number_density', 'stratospheric_NO2_column_number_density'])\
    .filterDate(begin, end).filterBounds(aoi)

if 'O3' in pollution_types:
    O3 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_O3')\
    .select('O3_column_number_density')\
    .filterDate(begin, end).filterBounds(aoi)

if 'SO2' in pollution_types:
    SO2 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_SO2')\
    .select('SO2_column_number_density')\
    .filterDate(begin, end).filterBounds(aoi)

if 'CH4' in pollution_types:
    CH4 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_CH4')\
    .select('CH4_column_volume_mixing_ratio_dry_air')\
    .filterDate(begin, end).filterBounds(aoi)

#Store the native resolution of the Sentinel-5P data 
native_scale = globals()[pollution_types[0]].first().projection().nominalScale().getInfo()

# Create a separate image collection by day for each pollution type
number_of_days = end.difference(begin, 'day')
def calculateDays(day):
    return begin.advance(day,'day')

list_of_days = ee.List.sequence(0, number_of_days.subtract(1)).map(calculateDays)

def create_mosaics(date, newlist):
    # Cast values
    date = ee.Date(date)
    newlist = ee.List(newlist)

    if 'NO2' in pollution_types:  # First since multiple bands
        filtered_day_no2 = NO2.filterDate(date, date.advance(1,'day'))
        image = ee.Image(filtered_day_no2.mosaic()).set({'Date': date})
        
    if 'UV' in pollution_types:
        filtered_day_uv = UV.filterDate(date, date.advance(1,'day'))
        band = ee.Image(filtered_day_uv.mosaic())
        if 'image' in locals():
            image = image.addBands(band)
        else:
            image = band
            
    if 'CO' in pollution_types:
        filtered_day_co = CO.filterDate(date, date.advance(1,'day'))
        band = ee.Image(filtered_day_co.mosaic())
        if 'image' in locals():
            image = image.addBands(band)
        else:
            image = band
            
    if 'CH2O' in pollution_types:
        filtered_day_ch2o = CH2O.filterDate(date, date.advance(1,'day'))
        band = ee.Image(filtered_day_ch2o.mosaic())
        if 'image' in locals():
            image = image.addBands(band)
        else:
            image = band
            
    if 'O3' in pollution_types:
        filtered_day_o3 = O3.filterDate(date, date.advance(1,'day'))
        band = ee.Image(filtered_day_o3.mosaic())
        if 'image' in locals():
            image = image.addBands(band)
        else:
            image = band
            
    if 'SO2' in pollution_types:
        filtered_day_so2 = SO2.filterDate(date, date.advance(1,'day'))
        band = ee.Image(filtered_day_so2.mosaic())
        if 'image' in locals():
            image = image.addBands(band)
        else:
            image = band
            
    if 'CH4' in pollution_types:
        filtered_day_ch4 = NO2.filterDate(date, date.advance(1,'day'))
        band = ee.Image(filtered_day_ch4.mosaic())
        if 'image' in locals():
            image = image.addBands(band)
        else:
            image = band
            
    filtered_day = globals()[pollution_types[0]].filterDate(date, date.advance(1,'day'))
    
    # Add the mosaic to a list only if the collection has images
    return ee.List(ee.Algorithms.If(filtered_day.size(), newlist.add(image), newlist))

daily_mosaics = ee.ImageCollection(ee.List(list_of_days.iterate(create_mosaics, ee.List([]))))

# If the scale of the smallest item in 'polygons' is less than the native resolution of the S5 data, then set the variable scale to the min scale of polygons, otherwise set it to the native resolution
def addArea(feature):
    return feature.set({'area': feature.geometry().area()})  
polygons_with_area = polygons.map(addArea)

min_polygon_area = polygons_with_area.reduceColumns(reducer=ee.Reducer.min(), selectors=['area']).getInfo()['min']

if min_polygon_area < (native_scale)**2:
    scale = max(10, math.sqrt(min_polygon_area)) # In case there are any polygons with very small area 
else: 
    scale = native_scale

# Calculate the pollution levels by area 
def zonalStats(image):
    date = image.get("Date")
    toReturn = image.reduceRegions(reducer=ee.Reducer.mean(), collection=polygons, scale=scale)
    return toReturn.set('Date', date)

zonal_stats = daily_mosaics.map(zonalStats)

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
