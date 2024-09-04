# GeoMap-Scoring-Tool
GeoMap Scoring Tool is a Python tool that calculates and visualizes region-based scores from map images. Users can upload a map and its legend to generate an interactive map where hovering reveals specific region scores. Ideal for geographic data analysis, it provides both overall and detailed region scores.

# Map Score Extractor
## Overview
Map Score Extractor is a versatile tool designed to help users extract numerical scores from various types of maps, where color-coded regions represent different values or categories. Whether you're a researcher, analyst, or professional dealing with maps that visually represent data without accompanying numerical values, this tool enables you to quantify and analyze the data with ease.

## Features
### Upload and Process Maps:
Easily upload maps and their associated legends to extract corresponding scores.
### Interactive Map Display: 
View and interact with the processed map, displaying the score of specific areas by hovering over them.
### Customizable Segmentation: 
Adjust the number of segments and score ranges based on your legend, allowing for flexible analysis of various map types.
### Black & White Map Support: 
Includes functionality for handling black and white maps by filtering out greyish pixels.

## Installation
To run this tool, you'll need Python and a few dependencies. You can install the required packages using the following command:
pip install numpy opencv-python matplotlib pandas tkintertable Pillow PyInstaller

## Usage
### Upload Legend and Map:

- Start the tool by running the Python script or using the provided python file in the GeoMap-Scoring-Tool folder .
- Upload the legend associated with the map. The tool will process this legend to understand the color-to-score mapping.
- Upload the map you want to analyze. The tool will process the map, allowing you to view and interact with it to see the scores of different regions.
  
### Interactive Score Extraction:

- Hover over different regions of the map to see the corresponding scores based on the legend.
- The tool segments the map into 10 areas by default (which can be changed), with scores ranging incrementally from 0 to 1.0 by default (which can also be changed as fit).
  
### Application:

This tool is highly adaptable and can be used for a variety of purposes. Whether you're working with environmental service maps, heatmaps, risk assessment maps, or any other visual representation of data, Map Score Extractor helps you translate these visual cues into actionable, quantitative data.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! If you have suggestions for improvements or find bugs, feel free to open an issue or submit a pull request.

## Acknowledgments
This tool was developed to address the challenge of extracting numerical data from visually represented maps. It aims to bridge the gap between visual and quantitative analysis, making it easier to work with map-based data across various fields.
