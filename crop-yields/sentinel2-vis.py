# -*- coding: utf-8 -*-

import ee 

ee.Initialize()

###############################################################
# ENTER USER INPUTS HERE  
###############################################################
plot_boundaries = ee.FeatureCollection() # Upload plot boundary data (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes
aoi = ee.FeatureCollection() # Upload AOI polygon (e.g. using the Google Earth Engine console) and insert the asset ID here, in single or double quotes
# The AOI can contain multiple polygons, but should be relatively simple. A bounding box or convex hull around all plot boundaries is appropriate

# Start and end dates for image search (YYYY-MM-DD)
begin = ee.Date() # E.g. '2019-08-01'
end = ee.Date() # E.g. '2019-12-15'

# Set max cloud cover (%)
max_cloud_cover = 10  # This is a default value. This value should be kept relatively small since high cloud cover can bias results.

# Minimum AOI coverage
min_aoi_coverage = 0.9 # This is the minimum area coverage of low cloud satellite tiles (< max_cloud_cover) calculated against AOI
# The percent of plots with data may be higher or lower since they may not be uniformly distributed in the AOI or plots may be beneath clouds 

# Reduction method
# One of 'mean', 'median', 'min', 'max', 'mode', 'sd'
reducer = 'mean'  # Each plot has multiple pixel values in it. This specifies how a single value should be extracted for each plot on each date.
# For example, if 'mean' is selected the average pixel value within a plot is calculated and passed to the CSV

# Export information (to Google Drive)
output_folder = 'EXAMPLE_FOLDER'  # Folder name to save outputs in Google drive. The folder should be created before running the script.
output_file = 'EXAMPLE_FILE_NAME' # Output file name  

##############################################################
# END USER INPUTS 
##############################################################

if reducer == 'median':
	ee_reducer = ee.Reducer.median()
elif reducer == 'mean':
	ee_reducer = ee.Reducer.mean()
elif reducer == 'min':
	ee_reducer = ee.Reducer.min()
elif reducer == 'max':
	ee_reducer = ee.Reducer.max()
elif reducer == 'sd':
	ee_reducer = ee.Reducer.srdDev()
else:
	raise Exception('Please select a valid reduction method.')


l2a = ee.ImageCollection("COPERNICUS/S2_SR")

# Filter the Sentinel-2 data based on AOI and cloud cover
filtered = l2a.filterDate(begin, end).filterBounds(aoi).filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 15))

# Create a separate image collection by day
number_of_days = end.difference(begin, 'day')
def calculateDays(day):
    return begin.advance(day,'day')

list_of_days = ee.List.sequence(0, number_of_days.subtract(1)).map(calculateDays)

"""
NOTE
Mosaicing defaults to EPSG:4326 with 1 degree by 1 degree scale by default if there are competing 
inputs. This doesn't appear to change the native resolution in this case, but reprojection
will need to occur here to standardize all band projections if the issue emerges. 
"""

def calc_footprint(image, list):
    # Cast
    image = ee.Image(image)
    list = ee.List(list)
    tile_footprint = ee.Algorithms.GeometryConstructors.Polygon(
        ee.Geometry( image.get('system:footprint') ).coordinates()
        )
    return list.add(ee.Feature(tile_footprint))


def create_mosaics(date, newlist):
    # Cast values
    date = ee.Date(date)
    newlist = ee.List(newlist)
    
    # Filter collection between date and the next day
    filtered_day = filtered.filterDate(date, date.advance(1,'day'))
    
    # Create a variable recording the footprint of the mosaic 
    footprint_collection = ee.FeatureCollection(ee.List(filtered_day.iterate(calc_footprint, ee.List([]))))
    footprint = ee.Feature(footprint_collection.union(100).first())
    
    # Generate the mosaic 
    image = ee.Image(filtered_day.mosaic()).set({'Date': date, 'footprint': footprint})
    
    # Add the mosaic to a list only if the collection has images
    return ee.List(ee.Algorithms.If(filtered_day.size(), newlist.add(image), newlist))

daily_mosaics = ee.ImageCollection(ee.List(list_of_days.iterate(create_mosaics, ee.List([]))))

# Only keep days where area coverage is at least 80%
if aoi.size().getInfo() == 1:
    aoi_footprint = aoi.first().geometry()
else:
    aoi_footprint = ee.Feature(aoi.union(100).first())

def add_coverage(image):
    footprint = ee.Feature(image.get('footprint'))
    image_footprint = footprint.geometry()
    aoi_area = aoi_footprint.area()
    intersect = aoi_footprint.intersection(image_footprint, ee.ErrorMargin(1))
    intersect_area = intersect.area()
    coverage = ee.Number(intersect_area.divide(aoi_area))
    return image.set('AOI_COVERAGE', coverage)
    
daily_mosaics_aoi = daily_mosaics.map(add_coverage)
final_imagery = daily_mosaics_aoi.filter(ee.Filter.gte('AOI_COVERAGE', min_aoi_coverage))

# Apply cloud and water mask
def mask_s2_image(image):
    # Cast
    image = ee.Image(image)
    scl = image.select("SCL")  # Scene classification map
    # Mask out satured or defective (1), cloud shadows (3), water (6), clouds medium prop (8), clouds high prob (9)
    mask = scl.neq(9).And(scl.neq(8)).And(scl.neq(6)).And(scl.neq(3).And(scl.neq(1)))
    return image.updateMask(mask)

    
masked_final_imagery = final_imagery.map(mask_s2_image)


# Extract vegetation indices (VIs) and relevant bands from the masked imagery, use separate functions for VIs that only use 10m imagery vs ones that use 20m 
def add_vis_10m(image):
    # NDVI 
    VIs = image.normalizedDifference(['B8', 'B4'])
    VIs = VIs.select("nd").rename("NDVI")
    # GCVI
    VIs = VIs.addBands(image.expression(
    '(NIR / GREEN) - 1', {
      'NIR': image.select('B8'),
      'GREEN': image.select('B3')
    }).rename('GCVI'))
    # EVI (note, bands are scaled by 10,000 which needs to be removed to get surface reflectance values)
    VIs = VIs.addBands(image.expression(
    '2.5*((NIR - RED) / ((NIR + 6 * RED - 7.5 * BLUE) + 1))', {
      'NIR': image.select('B8').divide(10000),
      'RED': image.select('B4').divide(10000),
      'BLUE': image.select('B2').divide(10000)
    }).rename('EVI'))
    # B4
    VIs = VIs.addBands(image.select('B4'))
    # B8
    VIs = VIs.addBands(image.select('B8'))
    return VIs.set({'Date': image.get("Date")})

def add_vis_20m(image):
    # Red-edge NDVI (Band 5 is 20m)
    VIs = image.normalizedDifference(['B8', 'B5'])
    VIs = VIs.select("nd").rename("reNDVI")
    # MTCI
    VIs = VIs.addBands(image.expression(
    '(NIR - RE) / (RE - RED)', {
      'NIR': image.select('B8'),
      'RE': image.select('B5'),
      'RED': image.select('B4')
    }).rename('MTCI'))
    #SeLI: Pasqualotto, N., Delegido, J., Van Wittenberghe, S., Rinaldi, M., & Moreno, J. (2019). Multi-Crop Green LAI Estimation with a New Simple Sentinel-2 LAI Index (SeLI). Sensors (Basel, Switzerland), 19(4), 904. doi:10.3390/s19040904
    VIs = VIs.addBands(image.normalizedDifference(['B8A', 'B5']).rename('SeLI'))
    #LAIgreen 
    VIs = VIs.addBands(image.expression('5.405 * ((R865 - R705) / (R865 + R705)) - 0.114', {
        'R865': image.select('B8A'),
        'R705': image.select('B5')
        }).rename("LAIgreen"))
    # B5
    VIs = VIs.addBands(image.select('B5'))
    # B8A 
    VIs = VIs.addBands(image.select('B8A'))
	return VIs.set({'Date': image.get("Date")})

vegetation_indices_10m = masked_final_imagery.map(add_vis_10m)
vegetation_indices_20m = masked_final_imagery.map(add_vis_20m)

# Calculate zonal stats for each VI/band
meters = 10 
def zonalStats(image):
    date = image.get("Date")
    toReturn = image.reduceRegions(reducer=ee_reducer, collection=plot_boundaries, scale=meters)
    return toReturn.set('Date', date)

zs_10m = vegetation_indices_10m.map(zonalStats)
meters = 20 
zs_20m = vegetation_indices_20m.map(zonalStats)


#  Remove geometry from the zonal stats
def processFeature(feature):
    return feature.setGeometry(None)

def removeGeometry(featureCollection):
    fc = ee.FeatureCollection(featureCollection)  # Cast
    fc_date = ee.Date(fc.get('Date')).format('yyyy-MM-dd')  # Get date to assign
    fc_no_geometry = fc.map(processFeature)
    toReturn = fc_no_geometry.map(lambda x: x.set({'Date': fc_date}))
    return toReturn

zs_10m_no_geom = zs_10m.map(removeGeometry).flatten()
zs_20m_no_geom = zs_20m.map(removeGeometry).flatten()


#  Merge all of the data together 
def cleanJoin(feature):
    return ee.Feature(feature.get('primary')).copyProperties(feature.get('secondary'))

filter = ee.Filter.equals(leftField = 'system:index', rightField = 'system:index')
simpleJoin = ee.Join.inner('primary', 'secondary')
zonal_stats = simpleJoin.apply(zs_10m_no_geom, zs_20m_no_geom, filter).map(cleanJoin)

# Export the data to Google Drive
task = ee.batch.Export.table.toDrive(collection=zonal_stats, description=output_file, 
                        fileFormat='CSV', fileNamePrefix=output_file,
                        folder=output_folder)

task.start()    

