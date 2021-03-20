# sentinel-5p.py 

This Python script calculates air quality values using data from the Sentinel-5P mission and the Google Earth Engine. 

## Setup 

You must register for the Google Earth Engine to run this code. To do so, go to [code.earthengine.google.com](code.earthengine.google.com) while signed into a Google account. If you are signed in with an academic or non-profit affiliated Gmail account (e.g. a .edu email address), the Google Earth Engine will be available for free. Otherwise, it is a paid service. 

A Python 3 installation is also required to run this code. We suggest using the Conda package manager to install Python and the required packages locally. Installation instructions are available at [https://developers.google.com/earth-engine/python_install-conda](https://developers.google.com/earth-engine/python_install-conda). These instructions also include information about how to authenticate the Google Earth Engine service. Make sure to get through the step involving `earthengine authenticate` prior to executing any of the code in this repository.

Although we suggest using a local installation, the Google Earth Engine also supports the use of Google Colab Notebooks that operate on the web. Instructions for using these notebooks are available at [https://developers.google.com/earth-engine/python_install-colab](https://developers.google.com/earth-engine/python_install-colab). The code included in this script can be used in a Colab Notebook with light modification. However, we do not offer any instructions or support for the Colab platform. 

## Description, inputs, and outputs 

**Description:** This file calculates air quality information using data from the European Space Agency's Sentinel-5P mission. The spacecraft collects data on the atmospheric concentrations of ozone, methane, formaldehyde, aerosol, carbon monoxide, nitrogen oxide, sulphur dioxide, and cloud information. The spatial resolution is 0.01 arc degrees -- corresponding to about 11.1 km at the equator -- 

**User inputs:** You must have boundary data, such as a shapefile or geojson, of the polygons for which you wish to collect wealth data. __Make sure that the plot boundary data has a unique identifier in the attribute table.__ The script outputs a csv containing panel data in long format. So a unique id is necessary to determine which polygon a data point was recorded in.

**Automatically pulled inputs:** The script uses Sentinel-5P data products hosted by the Google Earth Engine. 

For more information, visit [https://developers.google.com/earth-engine/datasets/catalog/sentinel-5p](https://developers.google.com/earth-engine/datasets/catalog/sentinel-5p). 

**Outputs:** The script outputs a CSV containing measurements of each air quality variable selected for satellite pass in the date range and each polygon. 

## Instructions 

1. Register for the Google Earth Engine, install Anaconda and Python 3, and authenticate the Google Earth Engine package following the instructions in the Setup section. 

- Import the boundary data (e.g. a shapefile or geojson) to the Google Earth Engine. The easiest way to do this is using the console at [https://code.earthengine.google.com/](https://code.earthengine.google.com/). Instructions are available at [https://developers.google.com/earth-engine/importing](https://developers.google.com/earth-engine/importing). 

- Specify the import path to the plot boundary Google Earth Engine asset in the `shapefile` variable in `sentinel-5p.py`. Instructions for finding the asset ID are available at [https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script](https://developers.google.com/earth-engine/asset_manager#importing-assets-to-your-script).

- Enter the begin and end date parameters via the `begin` and `end` variables in `sentinel-5p.py`.
	
- Specify a list of air quality metrics in the variable `pollution_types.` __Make sure to keep NO2.__ The script currently will not work without this variable, so I suggest keeping it and ignoring the data if you are not interested in it. Alternatively, you will need to edit the function `create_mosaics`.  

- Create a folder on your Google Drive account to store the output if an appropriate folder does not already exist. 

- Insert the folder name from step 9 in the variable `output_folder`. 

- Insert an output file name in the variable `output_file`. Do not include an extension. 

- Open a command line terminal and set your current directory to the directory containing `sentinel-5p.py`.

- Activate the conda environment that includes your Google Earth Engine Python installation. If you followed the setup instructions exactly, this can be accomplished by typing `conda activate ee`. 

- Enter `python sentinel-5p.py`. 

- The CSV output should be automatically exported to the folder that you specified. This can be downloaded and used in analysis. 

