#FUNCTIONS FOR PROJECT
import re
import plotly.express as px
import math
import pandas as pd
import random

print('entered my functions module!')

# function to determine if there is a decimal digit in a string
def contains_number(input_string):
    return bool(re.search(r'\d', input_string))

# determine if a string contains characters
def contains_letter(input_string):
    return bool(re.search(r'\D', input_string))

# Split a string into its lines
def split_into_rows(string):
    row_list = re.split(r'[\r\n]', string)
    no_empty_rows_list = [row for row in row_list if row]
    return no_empty_rows_list

# Split a line into it's cells
def split_into_cells(row):
    cell_list = re.split(',', row)
    return cell_list

# remove empty lines from a string. 
def remove_empty_lines(string):
    return re.sub(r'\n+', '\n', string).strip('\n')

# Search for a substring and return the line it is on
def search(string, search_substring):
    row_list = split_into_rows(string)
    row_index = 0
    for line in row_list:
        for i in range(len(line) - len(search_substring) + 1):
            compare_substring = line[i:i + len(search_substring)]
            if compare_substring == search_substring:
                #print(f'{compare_substring} found on row {row_index}')
                return row_list[row_index]
        row_index += 1
    else:
        print(f'{search_substring} not found')

# Pull out the value associated with a variable in the header section of the file
def pull_value(string, variable):
    row = search(string, variable)
    cell_list = split_into_cells(row)
    cell_index = cell_list.index(variable) + 1
    if contains_number(cell_list[cell_index]):
        return cell_list[cell_index]
    else:
        print(f'{variable} does not have an associated value.')

# Find the start of a table
def find_table_start(string, search_phrase):
    row_list = split_into_rows(string)
    print(f'row_list: {row_list}')

    try:
        start_row = row_list.index(search(string, search_phrase))
        print(f'start_row index: {start_row}')
        content_start_row = row_list[start_row]
        print(f'start_row contents: {content_start_row} and type: {type(content_start_row)}')
        print(f'number of columns: {content_start_row.count(",") + 1}')
    except ValueError as error:
        print(f'Error finding search_phrase "{search_phrase}": {error}')
        return -1
    
    next_row = row_list[start_row + 1]
    print(f'next_row: {next_row}')
    third_row = row_list[start_row + 2]
    print(f'third_row: {third_row}')
    print(f'first character in next_row: {next_row[0]}')
    print(f'first character in third_row: {third_row[0]}')

    if contains_letter(next_row[0]) and contains_number(third_row[0]):
        return start_row
    else:
        print(f'{start_row} is not the start of this table')
        return -1

# Find and replace a phrase
def find_and_replace(string, keyword_list, keyword_replacement_list):
    i = 0
    new_string = string
    for keyword in keyword_list:
        new_string = new_string.replace(keyword, keyword_replacement_list[i])
        i += 1
    return new_string


# scalar function to determine amount to increase an upper bound pulled from file header
# multiply by 20%, or + integer, whichever is greater.
def create_scalar(value):
    return max(value * 1.2, value + 0.1)

# Create sub-list
def filter_list(dataframe, variable_list, column_name):
    filtered = dataframe[dataframe[column_name].isin(variable_list)].reset_index()
    del filtered['index']
    return filtered

# change time in seconds variables to appropriate units
def change_time_unit(time):
    unit = 's'
    if time >= 60:  # more than 60 seconds
        time = round(time / 60, 1)  #minutes
        unit = 'min'
        if time >= 60:  #more than 60 minutes
            time = round(time / 60, 1)  # hours
            unit = 'hrs'
            if time >= 24:  # more than 24 hours
                time = round(time / 24, 1)  # days
                unit = 'days'
    return time, unit

# determine the length of time between samples taken
def find_interval(time_series):
    try:
        log_interval = (time_series.iloc[99] - time_series.iloc[0]) / 100
        return log_interval
    except IndexError as error:
        try:
            log_interval = (time_series.iloc[9] - time_series.iloc[0]) / 10
            return log_interval
        except IndexError as error:
            print(error)


# determine length of study
def find_study_length(time_series):
    study_period = time_series.iloc[time_series.size - 1] - time_series.iloc[0]
    print(study_period)
    return study_period

# alter a gps coordinate to protect privacy
def scrub(num, c):
    if num == -9999:
        return num
    else:
        return num + c

# randomly alter gps latitude and longitude to protect privacy
def scrub_gps(filepath):
    #save as a string
    with open(filepath, 'r') as file:
        text = file.read()

    #make a dataframe from it
    table_start_row = find_table_start(text, '(HH:MM:SS)') + 1
    text_rows = split_into_rows(text)
    header = text_rows[0:table_start_row]
    print(header)
    
    # return header to string
    header_string = '\n'.join(header) 

    df = pd.read_csv(filepath, skiprows=table_start_row)
    print(df.head())
    print('original gps data: ', df[['GPSlat', 'GPSlon', 'GPSalt']].head())

    # create random number to add to latitude and longitude, consistent for whole file
    lon_offset = random.uniform(0.005, 0.01)
    lat_offset = random.uniform(0.005, 0.01)

    #modify gps columns
    df['GPSlat'] = df['GPSlat'].apply(lambda x: scrub(x, lat_offset))
    df['GPSlon'] = df['GPSlon'].apply(lambda x: scrub(x, lon_offset))
    print('scrubbed gps data: ', df[['GPSlat', 'GPSlon']].head())
    
    return header_string, df

# go through header data to see if there is anything wierd about the file
def on_load(string, time_series):
    temp_array = []

    # split string to just the header section of the file
    end_index = string.find('SAMPLE LOG')

    if end_index != -1:
        header = string[0:end_index]
    print(f'HEADER STRING: {header}')

    # pull out necessary values
    sdm = int(pull_value(header, 'ShutdownMode'))
    rt_programmed = float(
        pull_value(header, 'ProgrammedRuntime')
    ) / 60 / 60  # convert runtime from seconds to hours, will programmed runtime always be in seconds?
    rt_sampled = float(pull_value(header, 'SampledRuntime'))
    rt_logged = float(pull_value(header, 'LoggedRuntime'))
    rt_calculated = find_study_length(time_series)
    end_charge = float(
        pull_value(header, 'EndBatteryCharge')
    )  # would the percent charge when the battery loses power be 0? or higher?
    end_volt = float(pull_value(header, 'EndBatteryVoltage'))
    vfr_programmed = float(pull_value(header, 'VolumetricFlowRate'))
    vfr_average = float(pull_value(header, 'AverageVolumetricFlowRate'))
    mass_sampled = float(pull_value(header, 'PM2_5SampledMass'))
    vol_sampled = float(pull_value(header, 'SampledVolume'))
    log_interval_programmed = int(pull_value(header, 'LogInterval'))
    dc_programmed = int(pull_value(header, 'DutyCycle'))

    try:
        log_interval_sampled = find_interval(time_series)
    except IndexError as error:
        print(error)


    #look at shutdown mode
    print(f'SHUTDOWN-MODE: {sdm}, {type(sdm)}')
    if sdm != 3:
        temp_array.append('Device did not shut down correctly. Reason: ')
    if sdm == 0:
        temp_array.append('unknown error\n')
    elif sdm == 1:
        temp_array.append('User pressed stop button\n')
    elif sdm == 2:
        temp_array.append('depleted battery\n')
    elif sdm == 3:
        temp_array.append('completed preset study duration\n')
    elif sdm == 4:
        temp_array.append('overheated\n')
    elif sdm == 5:
        temp_array.append('maxed out power at start-up\n')
    elif sdm == 6:
        temp_array.append('maxed out power during study\n')
    elif sdm == 7:
        temp_array.append('filter blocked during study\n')
    elif sdm == 8:
        temp_array.append('SD card removed\n')
    elif sdm == 9:
        temp_array.append('Device froze\n')

    # compare programmed runtime to logged runtime
    if round(rt_programmed) != round(rt_logged):
        temp_array.append(
            f'study did not finish predetermined study duration. It fell {round(rt_programmed - rt_logged, 1)} hours short.\n'
        )
    #compare logged runtime to calculated runtime
    if round(rt_logged) != round(rt_calculated / 60 /
                                  60):  # convert seconds to hours
        temp_array.append(
            f'The calculated study duration ({round(rt_calculated)} hours) is different from the listed study duration ({round(rt_logged)} hours).Your file may not be complete.\n'
        )

    # look at end battery voltage
    if end_volt < 2.8:
        temp_array.append('drained battery life before study ended.\n')

    # compare desired volumetric flow rate to average volumetric flow rate
    if round(vfr_programmed, 1) != round(vfr_average, 1):
        temp_array.append(
            f'Average volumetric flow rate ({round(vfr_average, 2)} liters/minute) does not match programmed volumetric flow rate ({round(vfr_programmed, 2)} liters/minute).\n'
        )

    # 2.5 sampled mass, sampled runtime, logged runtime, average volumetric flow rate, sampled volume, battery charge are all greater than 0
    sample_list = {
        'sampled mass': mass_sampled, 
        'sampling runtime': rt_sampled, 
        'logged runtime': rt_logged, 
        'average volumetric flow rate': vfr_average, 
        'sampled volume': vol_sampled,
        'end battery charge': end_charge
    }
    for v in sample_list.items():
        if v[1] <= 0:
            temp_array.append(f'Error: {v[0]} is 0 or less.\n')

    # total sampled volume equals the average volume * the study duration
    #SampledVolume (liters) = SampledRuntime (hours) x 60 (minutes/hour) x AverageVolumetricFlowRate (liters/min)
    vol_expected = rt_sampled * vfr_average * 60
    print(
        f'COMPARE TOTAL VOLUME: EQUAL: {math.isclose(vol_expected, vol_sampled, rel_tol=1e1)} vol_expected: {vol_expected}, vol_sampled: {vol_sampled}, diff: {vol_expected - vol_sampled}'
    )
    if not math.isclose(vol_expected, vol_sampled, rel_tol=1e1):
        temp_array.append(
            f'Issue with the total sample volume ({round(vol_sampled, 2)} liters, expected {round(vol_expected, 2)} liters).\n'
        )

    # correct log interval
    try:
        if round(log_interval_programmed) != round(log_interval_sampled):
            temp_array.append(
                f'Log interval ({round(log_interval_sampled)} seconds) does not match programmed log interval ({round(log_interval_programmed)} seconds).\n'
            )
    except TypeError as error:
        temp_array.append(f'file does not contain enough data entries to determine log interval (number of entries = {time_series.count()})')

    # Pumps are on as much as they are supposed to be
    # total volume = length of study (hrs) * 60 (min/hour) * average volumetric flow rate (liters/minute) * duty cycle (%) * .01 decimal/%
    print(f'DUTY CYCLE CHECK. THIS {round((rt_sampled * 60) * vfr_average * (dc_programmed * 0.01))} SHOULD EQUAL THIS {round(vol_sampled)}')
    if not math.isclose(((rt_sampled * 60) * vfr_average * (dc_programmed * 0.01)), vol_sampled, rel_tol=1e1):
        temp_array.append(
            f'The percent of time the pumps ran may be different than the programmed {dc_programmed}% of the time.\n'
        )

    return temp_array


# Alert if variable is outside of acceptable bounds
def check_bounds(boundary_dataframe, variable_list, column_name,
                 raw_data_dataframe, time_series, keyword_dataframe,
                 keyword_replacements_dataframe, string):
    filtered_boundaries = filter_list(
        boundary_dataframe, variable_list, column_name
    )  # make a smaller dataframe of only the variables of interest.
    print(f'FILTERED BOUNDARY DATAFRAME: {filtered_boundaries}')
    print(type(filtered_boundaries))

    log_interval = find_interval(time_series)
    study_period = change_time_unit(find_study_length(time_series))

    temp_array = []
    flag_array = []

    for index, row in filtered_boundaries.iterrows(
    ):  # go over inputted variables
        variable = filtered_boundaries.iloc[index, 0]
        print(F'!VARIABLE!: {variable}, type: {type(variable)}\n')

        low_limit = filtered_boundaries.iloc[
            index, 1]  #pull the low and high limits from the csv.
        print(F'!LOW LIMIT!: {low_limit}, type: {type(low_limit)}\n')

        high_limit = filtered_boundaries.iloc[index, 2]
        print(F'!HIGH LIMIT!: {high_limit}, type: {type(high_limit)}\n')

        if low_limit is None or math.isnan(
                low_limit):  #check to make sure the limits exist
            temp_array.append((f'{variable} low limit is not defined\n'))
        if high_limit is None or math.isnan(high_limit):
            temp_array.append((f'{variable} high limit is not defined\n'))
        else:  #if both limits exist, then
            # convert strings to numbers
            if type(low_limit) == str and contains_number(low_limit):
                low_limit = float(low_limit)
            if type(high_limit) == str and contains_number(high_limit):
                high_limit = float(high_limit)

            print(f'after conversion: {type(low_limit)}, {type(high_limit)}')

            count_low = 0
            count_high = 0

            # iterate over every value in dataframe
            for value in raw_data_dataframe[variable]:
                if value < low_limit:
                    count_low += 1
                elif value > high_limit:
                    count_high += 1

            # convert count to time
            try:
                time_low = change_time_unit(count_low * log_interval)
                time_high = change_time_unit(count_high * log_interval)
            except TypeError as error:
                log_interval = float(pull_value(string, 'LogInterval'))
                print(f'PREDETERMINED LOG INTERVAL: {log_interval}, {type(log_interval)}')
                time_low = change_time_unit(count_low * log_interval)
                time_high = change_time_unit(count_high * log_interval)

            temp_array.append(
                find_and_replace(
                    f'{variable} was below the expected range for {time_low[0]} {time_low[1]} and above the expected range for {time_high[0]} {time_high[1]} out of {study_period[0]} {study_period[1]}.\n',
                    keyword_dataframe, keyword_replacements_dataframe))

            flag_array.append({
                'Variable': variable,
                'Time below limit': time_low,
                'Time above limit': time_high,
                'Study Period': study_period
            })

    df = pd.DataFrame(flag_array)

    print(df)
    for line in temp_array:
        print(line)

    return temp_array, df

# function to see if a sensor was out of range
def is_out_of_bounds(dataframe, variable):
    out = False
    df = dataframe.set_index('Variable')

    print(
        f'BELOW LIMIT CELL: {df.loc[variable, "Time below limit"]} ABOVE LIMIT CELL: {df.loc[variable, "Time above limit"]}'
    )
    print(f'NUMBER PART OF TIME BELOW LIMIT: {df.loc[variable, "Time below limit"][0]}, TYPE: {type(df.loc[variable, "Time below limit"][0])}')

    if df.loc[variable, 'Time below limit'][0] > 0 or df.loc[variable, 'Time above limit'][0] > 0:  # access cell value of 'time below limit' and 'time above limit'. Only interested in value, not units, so access first item in tuple to compare to 0.
        out = True

    return out

def is_out_of_bounds_loop(dataframe, variable_list, column_name):
    #filter bounds dataframe for variables in list. Loop through dataframe to check if variable was out of bounds and add the answer to a list. for index, row in dataframe.iterrows():
    df = filter_list(dataframe, variable_list, column_name) #.set_index('Variable')
    temp_list = []

    for index, row in df.iterrows(
    ):  # go over inputted variables
        variable = df.iloc[index, 0]
        print(f'LOOP IN IS OUT OF BOUNDS FUNCTION. INDEX: {index}, ROW: {row}, VARIABLE: {variable}, TIME BELOW LIMIT: {row["Time below limit"][0]}')
        if row['Time below limit'][0] > 0 or row['Time above limit'][0] > 0:
            temp_list.append(True)
        else:
            temp_list.append(False)

    return temp_list

# function to highlight rows in stats table based on flags
def highlight_rows(row):
    variable = row['Variable']
    print(f'ENTERED HIGHLIGHT_ROWS FUNCTION. ROW VARIABLE: {variable}')
    if is_out_of_bounds(df_bounds, variable):
        return {'backgroundColor': '#E9D502'}
    else:
        return {'backgroundColor': 'white'}

# CALCULATE SUMMARY STATISTICS
def summary_stats(dataframe, variable_list, bounds_dataframe, keyword_list, keyword_replacement_list):
    filtered_list = dataframe[variable_list]
    print(filtered_list)
    print(type(filtered_list))
    temp_array = []

    for variable in filtered_list:
        avg = filtered_list[variable].mean()
        stdDev = filtered_list[variable].std()
        coefV = stdDev / avg

        quartiles = filtered_list[variable].quantile([0.25, 0.75])
        iqr = quartiles[0.75] - quartiles[0.25]

        #message = f'For {variable} the summary statistics are:\nMean: {round(avg,3)}\nStandard Deviation: {round(stdDev,3)}\nCoefficient of Variation: {round(coefV, 3)}\nInter-quartile range: {round(iqr, 3)}\n\n'
        #message = find_and_replace(message, df_keywords, df_keyword_replacements)
        temp_array.append({
            'Variable': find_and_replace(variable, keyword_list, keyword_replacement_list),
            'Mean': round(avg, 3),
            'Standard Deviation': round(stdDev, 3),
            'Coefficient of Variation': round(coefV, 3),
            'Inter-Quartile Range': round(iqr, 3),
            'beyondLimit': is_out_of_bounds(bounds_dataframe, variable)
        })

    df = pd.DataFrame(temp_array)
    print(df)

    return df


# SCATTERPLOT FUNCTION
def update_scatterplot(dataframe, selected_variables, selected_time_series):
    fig = px.scatter(
        dataframe,
        x=selected_time_series,
        y=selected_variables,
        title='Sensor and Environmental Metrics Over Study Period',
        width=1100,
        height=600
        )
    fig.update_layout(title_font_size=25,
                      template='ggplot2',
                      legend_title_text='Legend')
    return fig
