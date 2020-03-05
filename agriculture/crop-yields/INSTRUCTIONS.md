# sentinel2-vis.py 

This Python script calculates the values of several different vegetation indices (VIs) useful for measuring crop yields. The file takes plot boundary data and an AOI polygon or multipolygon as inputs and returns a CSV that is saved to Google Drive containing VI values for each plot on each date of imagery meeting filtering criteria. The script uses the Google Earth Engine which is free to academics and non-profit organizations. 

## Setup 

You must register for the Google Earth Engine to run this code. To do so, go to [code.earthengine.google.com](code.earthengine.google.com) while signed into a Google account. If you are signed in with an academic or non-profit affiliated Gmail account (e.g. a .edu email address), the Google Earth Engine will be available for free. Otherwise, it is a paid service. 

A Python 3 installation is also required to run this code. We suggest using the Conda package manager to install Python and the required packages locally. Installation instructions are available at [https://developers.google.com/earth-engine/python_install-conda](https://developers.google.com/earth-engine/python_install-conda). These instructions also include information about how to authenticate the Google Earth Engine service. Make sure to get through the step involving `earthengine authenticate` prior to executing any of the code in this repository.

Although we suggest using a local installation, the Google Earth Engine also supports the use of Google Colab Notebooks that operate on the web. Instructions for using these notebooks are available at [https://developers.google.com/earth-engine/python_install-colab](https://developers.google.com/earth-engine/python_install-colab). The code included in this script can be used in a Colab Notebook with light modification. However, we do not offer any instructions or support for the Colab platform. 

## Description, inputs, and outputs 

This script takes polygons defining the boundaries of agricultural plots and a polygon or multipolygon outlining an area of interest spanning all plots as inputs. The agricultural plot data should include a unique plot ID in the attribute data. The script then pulls Sentinel-2 Level-2A data from the Google Earth Engine and calculates a series of vegetation indices (VIs) that have been shown to be effective at measuring smallholder agricultural yields in recent academic papers. The Sentinel-2 platform includes 10m x 10m red, green, blue and near-infrared bands, and 20m x 20m red-edge infrared and shortwave infrared bands. The satellite constellation spans most of the globe and has a revisit rate of 5 days. Additional information about the Sentinel-2 imagery is available at [https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR). 

The script calculates the Normalized Difference Vegetation Index (NDVI), Enhanced Vegetation Index (EVI), Green Chlorophyll Vegetation Index (GCVI), Red-edge NDVI (reNDVI), Simple Sentinel-2 LAI Index (SeLI), a Green LAI estimate based on SeLI (LAIgreen), and individual band values for bands 2 (blue), 4 (red), 5 (red-edge infrared 1), 8 (near-infrared) and 8A (red-edge infrared 4). NDVI, GCVI, EVI, band 2, band 4, and band 8 are calculated using 10 meter by 10 meter imagery. All other indices and bands are calculated at 20 meters by 20 meters, and bands with a 10m x 10m resolution are reprojected before the calculation. For each cloud-free date and plot, the script calculates a summary statistic of the pixel values contained in the plot (e.g. mean). The code then exports a CSV containing panel data including attribute data from the plot boundary data (e.g. a unique identifier for plots), each of the VI/band values, and the date. This CSV can immediately be imported into statistical software and used to measure yields. 

The VIs can be translated into yield predictions using several different methods. For instance, Lobell et al. (2019a) regress ground-based yield on all the values of a VI observed over a season to obtain satellite yield measurements. Lobell et al. (2019b) take the maximum value observed over the season. Cole and Killeen (2020) separately predict yields using each satellite pass and then consider a panel of productivity data. Additionally, the best performing VI is likely to vary based on geography and crop. Typically, NDVI should be outperformed by other indices if satellite yields are effective, however. 

## Instructions 

1. Register for the Google Earth Engine, install Anaconda and Python 3, and authenticate the Google Earth Engine package following the instructions in the Setup section. 

2. Import plot boundary data (e.g. a shapefile or geojson) and AOI data (e.g. one or more bounding boxes around all plots in the sample) to the Google Earth Engine. The easiest way to do this is using the console at [https://code.earthengine.google.com/](https://code.earthengine.google.com/). Instructions are available at [https://developers.google.com/earth-engine/importing](https://developers.google.com/earth-engine/importing). 

3. Specify the import path to the plot boundary Google Earth Engine asset in the `plot_boundaries` variable in `sentinel2-vis.py`. Instructions for finding the asset ID are available at [https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script](https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script).

4. Specify the import path to the AOI asset in the `aoi` variable in `sentinel2-vis.py`.

5. Enter the begin and end date parameters via the `begin` and `end` variables in `sentinel2-vis.py`. These specify the earliest and latest search dates for Sentinel-2 images. All images in this range meeting the cloud parameter specified later will be used. 

6. Specify the maximum average cloud cover (as a percentage) for each satellite tile in the `sentinel2-vis.py` using the variable `max_cloud_cover`. A tile is a Sentinel-2 image with an area of 100km x 100km. Your plots will often include multiple tiles. This variable specifies the maximum percentage cloud cover that each tile can include. Cloud cover can reduce the quality of results even if a cloud is not over a plot, e.g. due to shadows, so this value should be kept small, e.g. 5-20. The value should not be set at 0 because all tiles typically include at least some cloud cover, and cloudy pixels are masked out of calculations. 

7. Specify the minimum AOI overlap between the satellite tiles and your AOI polygon using the variable `min_aoi_coverage`. This is a rough approximation of the coverage of your plots since plots are likely not uniformly distributed in your AOI and masking of cloudy pixels may reduce coverage. For each date, the code calculates the union of the footprints of each of the low-cloud tiles kept after the previous step, then examines what percent of the AOI this polygon covers. 

8. Select a reduction method and enter it as a string in the variable `reducer` in `sentinel2-vis.py`. This variable defines how the set of VI pixels contained within the boundaries of a plot for each date will be condensed into a single statistic. Common options are `mean` which averages the pixel values and `median` which takes the median. The other options are `min`, `max`, `mode`, and `sd` (standard deviation).

9. Create a folder on your Google Drive account to store the output if an appropriate folder does not already exist. 

10. Insert the folder name from step 9 in the variable `output_folder`. 

11. Insert an output file name in the variable `output_file`. Do not include an extension. 

12. Open a command line terminal and set your current directory to the directory containing `sentinel2-vis.py`.

13. Activate the conda environment that includes your Google Earth Engine Python installation. If you followed the setup instructions exactly, this can be accomplished by typing `conda activate ee`. 

14. Enter `python sentinel2-vis.py`. 

15. The CSV output should be automatically exported to the folder that you specified. This can be downloaded and used in analysis. 

# plot_rainfall.py 

This script calculates average daily rainfall (in mm/hr) for each day between start and end dates specified by the user. The rainfall data comes from NASA's Global Participation Measurement (GPM) v6 mission. The rainfall estimates are derived from a series of sources, including satellite data and rainfall gauges. This script only uses data from the final run which is suitable for analysis and available after a 3.5 month lag. Half-hourly rainfall snapshots are averaged into a daily average.

## Setup 

Please follow the setup instructions for [sentinel2-vis.py](#sentinel2-vis.py). 

## Description, inputs, and outputs 

This script uses plot boundary data as an input and returns a CSV containing daily rainfall values, in mm/hour, for each plot. Rainfall data is obtained from NASA's Global Participation Measurement (GMP) using the Integrated Multi-satellitE Retrievals for GPM (IMERG) algorithm. The algorithm incorporates satellite microwave and microwave-calibrated infrared estimates of rainfall. Data from ground gauges is also incorporated. 

The IMERG algorithm is run multiple times as data comes in. The final run has a lag of 3.5 months, but has the highest quality. This script currently only uses final run data to maximize accuracy, but could easily be modified to include other data sources by removing the code `.filterMetadata('status', 'equals', 'permanent')`. 

GPM data includes estimates of rainfall every half hour, in mm/hr units. All 48 half-hourly values are averaged together for each day. The output variable containing the daily rainfall average is called "mean" in the produced CSV. As with `sentinel2-vis.py`, this CSV will be inserted into a Google Drive folder. 

## Instructions 

1. Import plot boundary data (e.g. a shapefile or geojson) and AOI data (e.g. one or more bounding boxes around all plots in the sample) to the Google Earth Engine. The easiest way to do this is using the console at [https://code.earthengine.google.com/](https://code.earthengine.google.com/). Instructions are available at [https://developers.google.com/earth-engine/importing](https://developers.google.com/earth-engine/importing). 

2. Specify the import path to the plot boundary Google Earth Engine asset in the `plot_boundaries` variable in `sentinel2-vis.py`. Instructions for finding the asset ID are available at [https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script](https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script).

3. Specify the import path to the AOI asset in the `aoi` variable in `plot_rainfall.py`.

4. Enter the begin and end date parameters via the `begin` and `end` variables in `plot_rainfall.py`. These specify the earliest date for which rainfall data will be pulled and the end date. The end date will be excluded. 

5. Create a folder on your Google Drive account to store the output if an appropriate folder does not already exist. 

6. Insert the folder name from step 5 in the variable `output_folder`. 

7. Insert an output file name in the variable `output_file`. Do not include an extension. 

8. Open a command line terminal and set your current directory to the directory containing `plot_rainfall.py`.

9. Activate the conda environment that includes your Google Earth Engine Python installation. If you followed the setup instructions exactly, this can be accomplished by typing `conda activate ee`. 

10. Enter `python plot_rainfall.py`. 

11. The CSV output should be automatically exported to the folder that you specified. This can be downloaded and used in analysis. 

# References 

Shawn Cole and Grady Killeen. The promise of satellite yield measurements: Evidence from a randomized controlled trial in Gujarat. Working paper, 2020. 

David B Lobell, George Azzari, Marshall Burke, Sydney Gourlay, Zhenong Jin, Talip Kilic, and Siobhan Murray. Eyes in the Sky, Boots on the Ground: Assessing Satellite- and Ground-Based Approaches to Crop Yield Measurement and Analysis. American Journal of Agricultural Economics, 10 2019a. ISSN 0002-9092. doi: 10.1093/ajae/aaz051. URL https://academic.oup.com/ajae/advance-article/doi/10.1093/ ajae/aaz051/5607565.

David B. Lobell, Stefania Di Tommaso, Calum You, Ismael Yacoubou Djima, Marshall Burke, and Talip Kilic. Sight for Sorghums: Comparisons of Satellite- and Ground-Based Sorghum Yield Estimates in Mali. Remote Sensing, 12(1):100, 12 2019b. ISSN 2072-4292. doi: 10.3390/rs12010100. URL https://www.mdpi.com/ 2072-4292/12/1/100.
