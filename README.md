**Air Quality Analyzer**
This application analyzes air quality log files for complete and reliable data. 

**Background**
The purpose of this project is to automate Quality Assurance and Quality Control (QAQC) on data from air quality devices. The application allows users to see the results of air quality studies and determine the accuracy and reliability of the data (QAQC). 

Researchers at the Center for Energy Development and Health are studying the air quality to which individuals are exposed, especially in the developing world. One experimental design asks participants to wear devices that monitor air quality for a set sample duration in which the device tracks particulate matter in the air and location data. It also measures environmental metrics such as temperature and device metrics such as battery power. 

This application looks at the data from those devices, cleans and processes it, checks for completeness and incongruencies, and then displays the data visually and statistically. The user can select measured metrics to plot on a scatterplot. Doing so automatically calculates summary statistics and the amount of time that variable measured outside of an expected range. 

**Dependencies**
Dash
Threading
Pandas
Traceback
Logging
Base64
IO
re
math
Plotly
