# viirs_nightlights.py 

This Python script calculates average nighttime light data from VIIRS Nighttime Day/Night Band Composites Version 1 monthly composites using the Google Earth Engine. 

## Setup 

You must register for the Google Earth Engine to run this code. To do so, go to [code.earthengine.google.com](code.earthengine.google.com) while signed into a Google account. If you are signed in with an academic or non-profit affiliated Gmail account (e.g. a .edu email address), the Google Earth Engine will be available for free. Otherwise, it is a paid service. 

A Python 3 installation is also required to run this code. We suggest using the Conda package manager to install Python and the required packages locally. Installation instructions are available at [https://developers.google.com/earth-engine/python_install-conda](https://developers.google.com/earth-engine/python_install-conda). These instructions also include information about how to authenticate the Google Earth Engine service. Make sure to get through the step involving `earthengine authenticate` prior to executing any of the code in this repository.

Although we suggest using a local installation, the Google Earth Engine also supports the use of Google Colab Notebooks that operate on the web. Instructions for using these notebooks are available at [https://developers.google.com/earth-engine/python_install-colab](https://developers.google.com/earth-engine/python_install-colab). The code included in this script can be used in a Colab Notebook with light modification. However, we do not offer any instructions or support for the Colab platform. 

## Description, inputs, and outputs 

**Description:** This file calculates average nighttime light levels for each region defined in the inserted shapefile. This output is frequently used to approximate GDP. A value is calculated for each month in the date range provided. The script is intended to work at the global level (e.g. values by nation), the nation level (e.g. values by state), the regional level (e.g. values by country), or the local level (e.g. values by town). 

**User inputs:** You must have boundary data, such as a shapefile or geojson, of the polygons for which you wish to collect wealth data. 

**Automatically pulled inputs:** The script uses VIIRS Nighttime Day/Night Band Composites Version 1 monthly composites hosted by the Google Earth Engine. The monthly composites exclude stray light from sources such as the moon and lightning. However, other stray light sources, in particular biomass burning, are not excluded. This can create a significant problem, particularly in areas where crop burning is prevalent. An annual composite product that removes these stray light sources is released for some years. However, it has not been updated since 2016 so we did not include code to use these. 

For more information, visit [https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG). 

**Outputs:** The script outputs a CSV containing average luminosity values for each month in the date range anf each polygon. 

## Instructions 

1. Register for the Google Earth Engine, install Anaconda and Python 3, and authenticate the Google Earth Engine package following the instructions in the Setup section. 

2. Import the boundary data (e.g. a shapefile or geojson) to the Google Earth Engine. The easiest way to do this is using the console at [https://code.earthengine.google.com/](https://code.earthengine.google.com/). Instructions are available at [https://developers.google.com/earth-engine/importing](https://developers.google.com/earth-engine/importing). 

3. Specify the import path to the plot boundary Google Earth Engine asset in the `shapefile` variable in `viirs_nightlights.py`. Instructions for finding the asset ID are available at [https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script](https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script).

4. Enter the begin and end date parameters via the `begin` and `end` variables in `viirs_nightlights.py`.

5. Specify a value for `resolution`. This must be either `global`, `national`, `regional`, or `local`. 

	- **WARNING:** The resolution parameter controls the scale that analysis is performed at, in meters, and the `tileScale` parameter in the reduce regions. If the first value is too small and the second is too large, then the Google Earth Engine job will fail because memory usage is too high or the compute time is too long. If the values are too large, then results may be noisy or inaccurate. The parameters are currently educated guesses and likely to face issues. You may change the `scale` and `tileScale` variables yourself in the script to see how results change. Please submit a new issues on Github if you face issues because of these values or have suggestions about what they should be.

6. Specify a value for `min_passes` in `viirs_nightlights.py`. This specifies the minumum number of cloud free data points that must have gone into creating a pixel for it to be kept. It must be at least 1. A higher value ensures higher data quality but may lead to lower coverage. 

7. Create a folder on your Google Drive account to store the output if an appropriate folder does not already exist. 

8. Insert the folder name from step 9 in the variable `output_folder`. 

9. Insert an output file name in the variable `output_file`. Do not include an extension. 

10. Open a command line terminal and set your current directory to the directory containing `viirs_nightlights.py`.

13. Activate the conda environment that includes your Google Earth Engine Python installation. If you followed the setup instructions exactly, this can be accomplished by typing `conda activate ee`. 

14. Enter `python viirs_nightlights.py`. 

15. The CSV output should be automatically exported to the folder that you specified. This can be downloaded and used in analysis. 

