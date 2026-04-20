# **Air Quality Analyzer**

This application analyzes air quality log files for complete and reliable data. 

??? Badge for python, badge for project status:active. Use shields.io

## **Description**

### Purpose
The purpose of this project is to automate Quality Assurance and Quality Control (QAQC) on data from air quality devices. The application allows users to see the results of air quality studies and determine the accuracy and reliability of the data (QAQC). 

### Background
Researchers at the Center for Energy Development and Health are studying the air quality to which individuals are exposed, especially in the developing world. One experimental design asks participants to wear devices that monitor air quality for a set sample duration in which the device tracks particulate matter in the air and location data. It also measures environmental metrics such as temperature and device metrics such as battery power. 

### What this program does
This application looks at the data from those devices, cleans and processes it, checks for completeness and incongruencies, and then displays the data visually and statistically. The user can select measured metrics to plot on a scatterplot. Doing so automatically calculates summary statistics and the amount of time that variable measured outside of an expected range. 

**Note**: Personally identifiable information in the example datasets are scrubbed to protect the privacy of participants. 

### Impact
Researchers can quickly determine if a study ran short, if the device died or malfunctioned during the study, and if any variables were measured out of an expected range. This helps determine the completeness, accuracy and trustworthiness of the study results. Researchers can also use the program for exploratory analysis of the data to understand what the participants’ air quality is like in their daily life.

## **Demo**

??? image of the landing page
??? image of the page once a log file is loaded
??? Video of using the page

## **Installation**

Clone this repo and install dependencies:

??? Code for how to do this

## **How to Use**

1. Run app.py:

??? code

2. Follow url in terminal:

??? Show screenshot of what/where this is

3. Click button on landing page and use a file in the example_data folder:

??? Show screenshot of what/where this is

4. Interact with the page. 
- **Table**: Hide/display variables in the table. Scroll down or across the table to see values. Hover over the column headings to see a short description of the heading.
- **Scatterplot**: Radio button to select the way time is displayed on the x-axis, local time, UTC time, or sample time. Dropdown selection to view different device metrics on the y-axis. Selecting device metrics automatically displays for how long that metric was outside of it's expected range and a row in the summary statistics table. This tells researchers how reliable and accurate the sensor data is.

## **Features**

- Function that automatically checks completeness of data
- Interactive table
- Interactive scatterplot
- Function that checks for accuracy of data by comparing values to an expected range
- Table of summary statistics

## **Built With**

- Python
- Pandas
- Plotly
- Dash

## **Future Features**

- **More QA/QC checks**: a function that alerts researchers to long periods where the device read 0, or the exact same value, indicating possible sensor failure. 
- **Participant compliance**: feature that determines if participants wore their air quality monitoring devices throughout the study period.
- **Data engineering**: Load multiple log files at the same time, aggregate the data, and store in a database.
- **Visualizations for air quality data**: scatterplot of particulate matter concentration, air quality heat map

## **Acknowledgments**
Thanks to my mentor, [Dr. Christian L'Orange](https://www.engr.colostate.edu/me/faculty/dr-christian-lorange/), for guiding me through this project. 