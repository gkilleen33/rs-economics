# Remote sensing scripts for economics 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**NOTE: This repository is still under development and has not been officially released. If you decide to use it and run into an issue, please submit an issue on Github to provide feedback.**

This repository contains open source scripts for utilizing remote sensing data in economics. The aim of this project is to reduce barriers to generating remote sensing and GIS data so that academics can take advantage of these data sources without investing time to learn in detail about the methods, figure out how to code solutions, or invest in specialized resources. 

All of the scripts in this repository are designed to run with minimal coding experience. They include step-by-step instructions in the `README.md` files that explain how to install any required software and generate results. Whenever possible, cloud computing platforms are used to minimize software installation and hardware requirements. We take particular advantage of the Google Earth Engine which is free to academics and employees of non-profit organizations. 

## Vector data structure for most Earth Engine scripts 

Most scripts that use the Google Earth Engine produce a panel data set in long form. As a result, it is important that the vector data (e.g. shapefile) that you upload to the Google Earth Engine contains a unique identifier for each polygon. This should be added as an attribute to the shapefile or other vector data format. 

## Contributing 

We welcome community contributions to this repository. Please note that any code contributed will fall under the MIT license that governs this repository, so it will be open source. Please see the license for more details. 

You may not upload proprietary code to the repository. In addition, make sure to provide proper credit if code is inspired by a paper or was used in a paper. If you are uploading scripts from an academic paper, we encourage you to provide citation information so that anyone that uses the scripts can easily provide credit. 

We encourage academics and data scientists to upload code to accomplish tasks that are not currently covered by this repository or improvements on existing functionality. We are hopeful that this repository will evolve into a hub where economists share remote sensing and GIS code from their projects and will surpass what we have included. If you have any questions, please submit an issue on Github. 

Users are also encouraged to suggest improvements, flag bugs, and propose modifications to existing code. If you are not comfortable with coding, please submit an issue. If you are comfortable with coding, then you are welcome to submit a pull request. 

We particularly appreciate suggested edits to instructions. Writing detailed documentation is quite time consuming, and it can be difficult to include sufficient details about processes that we are very comfortable with. Hence, edits to instructions can help other users make use of these resources and allow us to generate more content. 

For more details about contributing, including instructions, [click here](.github/CONTRIBUTING.md). 




