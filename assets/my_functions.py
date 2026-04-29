#FUNCTIONS FOR PROJECT
import re
import plotly.express as px
import math
import pandas as pd
import random

print('entered my functions module!')

# function to determine if there is a decimal digit in a string
def contains_number(input_string: str) -> bool:
    """Check a string for at least one instance of a number (decimal digit)."""
    return bool(re.search(r'\d', input_string))

# determine if a string contains characters
def contains_letter(input_string: str) -> bool:
    """Check a string for at least one instance of a letter."""
    return bool(re.search(r'\D', input_string))

# Split a string into its lines
def split_into_rows(string: str) -> list[str]:
    """Split a string into its rows and remove empty rows."""
    row_list = re.split(r'[\r\n]', string)
    no_empty_rows_list = [row for row in row_list if row]
    return no_empty_rows_list

# Split a line into it's cells
def split_into_cells(row: str) -> list[str]:
    """Split a row on every comma to get a list of the cells in that row."""
    cell_list = re.split(',', row)
    return cell_list

# remove empty lines from a string. 
def remove_empty_lines(string: str) -> str:
    """Remove empty lines from a string."""
    return re.sub(r'\n+', '\n', string).strip('\n')

# Search for a substring and return the line it is on
def search(string: str, search_substring: str) -> int | None:
    """
    Search for a substring in a string and return the line of the string it is on. If the substring is not found, print a message.
    
    Args:
        string (str): The string to search through.
        search_substring (str): The substring to search for.

    Returns:
        int: The index of the line containing the substring.
        Returns None and a terminal message if search was unsuccessful. 
    """
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
def pull_value(string: str, variable: str) -> str | None:
    """
    Pull out the value associated with a variable in the header section of the file.

    Args:
        string (str): The string to search through.
        variable (str): The variable to search for.

    Returns:
        str: The raw string value associated with the variable.
        Returns None and a terminal message if the variable has no associated value (defined as containing at least 1 number/digit).
        Callers are responsible for converting to numeric type if needed.
    """
    row = search(string, variable)
    cell_list = split_into_cells(row)
    cell_index = cell_list.index(variable) + 1
    if contains_number(cell_list[cell_index]):
        return cell_list[cell_index]
    else:
        print(f'{variable} does not have an associated value.')

# Find the start of a table
def find_table_start(string: str, search_phrase: str) -> int | None:
    """
    Find the index of the row that is the start of a table within a string. 

    Where the start of the table has a row for units, followed by a row for column headers, followed by the first row of data.
    Where data is floating point numbers. If the search phrase is found and the following rows match the expected format, return the index of the starting row of the table.
    

    Args:
        string (str): The string to search through.
        search_phrase (str): The phrase to search for.

    Returns:
        int: The index of the row that is the start of the table.
        Returns None and a terminal message if the start of the table was not found.
    """
    row_list = split_into_rows(string)
    #print(f'row_list: {row_list}')

    try:
        start_row = row_list.index(search(string, search_phrase))
        #print(f'start_row index: {start_row}')
        #content_start_row = row_list[start_row]
        #print(f'start_row contents: {content_start_row} and type: {type(content_start_row)}')
        #print(f'number of columns: {content_start_row.count(",") + 1}')
    except ValueError as error:
        print(f'Error finding search_phrase "{search_phrase}": {error}')
        return -1
    
    next_row = row_list[start_row + 1]
    #print(f'next_row: {next_row}')
    third_row = row_list[start_row + 2]
    #print(f'third_row: {third_row}')
    #print(f'first character in next_row: {next_row[0]}')
    #print(f'first character in third_row: {third_row[0]}')

    if contains_letter(next_row[0]) and contains_number(third_row[0]):
        return start_row
    else:
        print(f'{start_row} is not the start of this table')
        return None

# Find and replace a phrase
def find_and_replace(string: str, keyword_list: pd.Series, keyword_replacement_list: pd.Series) -> str:
    """
    Find and replace keywords with more readable names for the keyword.

    Args:
        string (str): the string to search through.
        keyword_list (pd.Series): the original keywords in the string that we want to replace.
        keyword_replacement_list (pd.Series): the new, more readable keywords that map to the original keywords.

    Returns:
        str: the string with the replaced keywords
    """
    i = 0
    new_string = string
    for keyword in keyword_list:
        new_string = new_string.replace(keyword, keyword_replacement_list[i])
        i += 1
    return new_string


# scalar function to determine amount to increase an upper bound pulled from file header
# multiply by 20%, or + integer, whichever is greater.
def create_scalar(value: float) -> float:
    """
    Increase an upper bound on a measured metric to flag values above the upper bound as suspicious.
    
    Note: not used in this project yet. Future way to more dynamically assign bounds.
    """
    return max(value * 1.2, value + 0.1)

# Create sub-list
def filter_list(dataframe: pd.DataFrame, variable_list: list[str], column_name: str) -> pd.DataFrame:
    """
    Create a sub-dataframe of specific variables from a larger dataframe.

    Args:
        dataframe (pd.Dataframe): original dataframe to search through.
        variable_list (list[str]): list of the variables to include in the filtered dataframe.
        column_name (str): The name of the column to search for matches against variable_list.
        Rows in the dataframe where this column's value appears in variable_list are kept in the returned dataframe.

    Returns:
        pd.Dataframe: dataframe filtered to only include variables from the specified list that appear in the specified column.
    """
    filtered = dataframe[dataframe[column_name].isin(variable_list)].reset_index()
    del filtered['index']
    return filtered

# change time in seconds variables to appropriate units
def change_time_unit(time: float) -> tuple[float, str]:
    """
    Convert a time value in seconds to the most readable unit. 

    Converts seconds to minutes, hours, or days depending on magnitude,
    rounding to one decimal place.

    Args:
        time (float): time in seconds

    Returns:
        tuple[float, str]: (converted_time, unit) where unit is one of 's', 'min', 'hrs', 'days'

    Example:
        >>> change_time_unit(3700)
        (1.0, 'hrs')
    """
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
def find_interval(time_series: pd.Series) -> int | None:
    """
    Determine how often the sensor is measuring data.

    It first calculates the average interval between taking samples using 100 rows of data.
    If there are fewer than 100 rows of data, it calculates the average log interval with 10 rows.
    If there are fewer than 10 rows, it prints an Index Error to the terminal.

    Args:
        time_series (pd.Series): column in the recorded data keeping track of Unix Time

    Returns:
        int: the average length of time in seconds between samples logged by the sensor.
        Returns None if there are fewer than 10 recorded entries.
    """
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
def find_study_length(time_series: pd.Series) -> int:
    """Determine how long the sensor ran for."""
    study_period = time_series.iloc[time_series.size - 1] - time_series.iloc[0]
    print(study_period)
    return study_period

# alter a gps coordinate to protect privacy
def scrub(num: float, c: float) -> float:
    """
    Alter a number.

    If a number is not defined (-9999), then it is not changed.
    """
    if num == -9999:
        return num
    else:
        return num + c

# randomly alter gps latitude and longitude to protect privacy
def scrub_gps(filepath: str) -> tuple[str, pd.DataFrame]:
    """
    Randomly alter GPS latitude and longitude to protect privacy.

    This function was used on the example data files accessible in the directory.
    It is not actively used while running app.py.

    Args:
        filepath (str): filepath pointing to a csv file to alter.

    Returns: 
        tuple[str, pd.Dataframe]: (header section of file, table section of file) with 
        table columns with altered GPS values (consistently altered for each file).
    """
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

# go through header data to see if there is anything weird about the file
def on_load(string: str, time_series: pd.Series) -> list[str]:
    """
    Perform completness and reliability checks on a newly loaded log file.
    
    Examines the header section of the file for signs of incomplete runtimes,
    device malfunction, or data inconsistencies. Checks include shutdown mode,
    runtime comparisons, battery levels, and compares programmed values to actual values.

    Args:
        string (str): The full raw text of the log file.
        time_series (pd.Series): column in the recorded data keeping track of Unix Time,
        used to calculate actual study duration and actual log interval.

    Returns:
        list[str]: list of human-readable alert messages describing any issues found.
    """
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
def check_bounds(boundary_dataframe: pd.DataFrame, variable_list: list[str], column_name: str,
                 raw_data_dataframe: pd.DataFrame, time_series: pd.Series, keyword_dataseries: pd.Series,
                 keyword_replacements_dataseries: pd.Series, string: str) -> tuple[list[str], pd.DataFrame]:
    """
    Alert the user if a measured variable is outside of an acceptable range.

    Args:
        boundary_dataframe (pd.Dataframe): table of variables with their associated lower and upper limits.
        variable_list (list[str]): list of variables to check.
        column_name (str): The name of the column to search for matches against variable_list.
            Rows in the dataframe where this column's value appears in variable_list are kept in the returned dataframe.
        raw_data_dataframe (pd.Dataframe): The dataframe to compare raw data values to the lower and upper limits for each variable.
        time_series (pd.Series): column in the recorded data keeping track of Unix Time,
            used to calculate actual study duration and actual log interval.
        keyword_dataseries (pd.Series): a list of variable names from the log file that we want to replace with more understandable names.
        keyword_replacements_dataseries (pd.Series): the new, more readable variable names that map to the original variable names.
        string (str): The full raw text of the log file. Used to find the programmed log interval in the header section in case the calculated log interval cannot be calculated.

    Returns:
        tuple[list[str], pd.Dataframe]: 
            - list[str]: human-readable alert messages describing how long each variable was below or above its expected range.
            - pd.Dataframe: One row per variable assessed, with columns:
                'Variable', 'Time below limit', 'time above limit', 'study period'.
                Time values are tuples of (value, unit) from the change_time_unit() method.
    """
    filtered_boundaries = filter_list(
        boundary_dataframe, variable_list, column_name
    )  # make a smaller dataframe of only the variables of interest.
    #print(f'FILTERED BOUNDARY DATAFRAME: {filtered_boundaries}')
    #print(type(filtered_boundaries))

    log_interval = find_interval(time_series)
    study_period = change_time_unit(find_study_length(time_series))

    temp_array = []
    flag_array = []

    for index, row in filtered_boundaries.iterrows(
    ):  # go over inputted variables
        variable = filtered_boundaries.iloc[index, 0]
        #print(F'!VARIABLE!: {variable}, type: {type(variable)}\n')

        low_limit = filtered_boundaries.iloc[
            index, 1]  #pull the low and high limits from the csv.
        #print(F'!LOW LIMIT!: {low_limit}, type: {type(low_limit)}\n')

        high_limit = filtered_boundaries.iloc[index, 2]
        #print(F'!HIGH LIMIT!: {high_limit}, type: {type(high_limit)}\n')

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

            #print(f'after conversion: {type(low_limit)}, {type(high_limit)}')

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
                    keyword_dataseries, keyword_replacements_dataseries))

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
def is_out_of_bounds(dataframe: pd.DataFrame, variable: str) -> bool:
    """
    Boolean check if a variable was out of range
    Note: still working on this function, going to use for highlighting rows function which is not yet working.
    """
    out = False
    df = dataframe.set_index('Variable')

    print(
        f'BELOW LIMIT CELL: {df.loc[variable, "Time below limit"]} ABOVE LIMIT CELL: {df.loc[variable, "Time above limit"]}'
    )
    print(f'NUMBER PART OF TIME BELOW LIMIT: {df.loc[variable, "Time below limit"][0]}, TYPE: {type(df.loc[variable, "Time below limit"][0])}')

    if df.loc[variable, 'Time below limit'][0] > 0 or df.loc[variable, 'Time above limit'][0] > 0:  # access cell value of 'time below limit' and 'time above limit'. Only interested in value, not units, so access first item in tuple to compare to 0.
        out = True

    return out

def is_out_of_bounds_loop(dataframe: pd.DataFrame, variable_list: list[str], column_name: str) -> list[bool]:
    """
    Boolean check on multiple variables to see if they went out of range during the study period
    Note: still working on this function, going to use for highlighting rows function which is not yet working.
    """
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
def highlight_rows(row, bounds_dataframe):
    """
    Highlight rows in the summary_stats table if a variable in it was flagged for being out of range.
    Note: still working on this function, not yet working.
    """
    variable = row['Variable']
    print(f'ENTERED HIGHLIGHT_ROWS FUNCTION. ROW VARIABLE: {variable}')
    if is_out_of_bounds(bounds_dataframe, variable):
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
