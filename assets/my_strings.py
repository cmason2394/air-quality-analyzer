print('entered my strings module!')

title = 'Air Quality Data'
welcome = 'Welcome to the air quality data visualization page.'
purpose = 'The purpose of this site is to process the results of air quality studies for quality assurance and quality control.'
begin = 'To begin, select the air quality results file you wish to process.'
title_table1 = 'Collected Sensor Data'
select1 = 'Select a time series: '
select2 = 'Select sensor data: '
flags_guiding_text = '''When a variable goes out of range, it means the measured data was above or below a limit defined as reasonable for that variable.
 This does not mean that data is inherently incorrect. For example, very hot or cold days could be outside the set limit for temperature.
 However, it does mean you should take a closer look at your data to see if it makes sense.'''
mean_explanation = 'the average of a dataset. Measures where the middle of the data lies.\n'
stdDev_explanation = 'average distance of data points from the mean. The larger the standard deviation, the bigger the spread of data from middle.\n'
coefV_explanation = 'percentage representation of standard deviation. Useful for comparing variation between studies and between variables with different units.\n'
iqr_explanation = '''the spread of the middle 50% of the data. The difference between the top of the middle and the bottom of the middle. 
 Larger values indicate a wider spread of the middle 50% of the data. Smaller values indicate a narrow variation of the middle 50% of the data.\n'''
