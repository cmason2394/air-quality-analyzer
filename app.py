"""Main application file for the air quality data analysis dashboard. Contains the layout of the dashboard and callback functions for interactivity. Stores structured data used to build the dashboard."""

# import necessary libraries
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import threading
import pandas as pd
import traceback
import logging
import assets
from assets import my_functions as mf
from assets import my_strings as strings
import base64
import io

# Initialize global variables, stored at global scope to be used across multiple callback functions and avoid reloading dataframes and other variables multiple times.
# These variables are updated in the first callback function when the user uploads a file, and then used in subsequent callbacks for the scatterplot, alert function, and summary statistics.
file_path = "" #filepath of the uploaded file, stored as a string
df_relevant = pd.DataFrame() # dataframe containing all relevant data for the project, excludes columns that are beyond the scope of this project. Rounded to 1 decimal place for easier interpretation and to avoid false precision.
df_believable = pd.DataFrame() # dataframe of data that helps determine whether the data is believable (complete and accurate). Contains a subset of the columns in df_relevant related to device information and enviromental metrics.
df_units = pd.DataFrame() # dataframe that contains the relevant variable names and their units of measurement
ds_time = pd.Series(dtype=int) # pandas dataseries of integers containing Unix time values during the study, used to determine study length and how long a variable was beyond its boundaries.
df_boundary_numbers = pd.read_csv('assets/boundary_numbers.csv')  #relative file path # dataframe containing the upper and lower bounds for each variable, used in the alert function to determine whether a variable is beyond its boundaries.
df_dictionary = pd.read_csv('assets/glossary.csv', index_col='Variables')  #relative file path # dataframe containing the variable names, their units of measurement, and descriptions, used to create tooltips and make the dashboard more user-friendly by showing readable names instead of variable names.
ds_keywords = df_dictionary.index.to_series() # pandas dataseries of the variable names from the glossary, used to replace variable names with readable names.
ds_replacements = df_dictionary['Readable Name'] # pandas dataseries of the readable names from the glossary, used to replace variable names with readable names in the dashboard and make it more user-friendly.

#print('my functions module', str(mf.find_table_start))
#print(f'dictionary dataframe: {df_dictionary.head()}')
#print(f'keywords: {ds_keywords.head()}')
#print(f'readable names: {ds_replacements.head()}')

# Initialize Dash app and define app layout
# Layout contains: title, welcome message, file upload button, and output div
# Output div is populated dynamically by the select_file callback
app = dash.Dash(__name__, suppress_callback_exceptions=True)

#app title
app.title = strings.title

app.layout = html.Div([
    html.H1(strings.title),
    html.P(strings.welcome + ' ' + strings.purpose + '\n' + strings.begin),
    dcc.Upload(
        id="upload-data",
        children=html.Button("Select File"),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id="output")
])


# first callback function when the user uploads a file
@app.callback(Output("output", "children"),
              [Input("upload-data", "contents")])
def select_file(contents: str):
    """
    Callback function that is triggered when the user uploads a file. 
    
    Attempts to parse and process the uploaded file, returning an error message if the file format is not supported or cannot be read.
    If supported and readable, it processes the data and updates the dashboard with the relevant information. 

    Args:
        contents (str): The contents of the uploaded file, encoded in base64.
    
    Returns:
        A tuple of different HTML elements: 
            html.Div: file information and results of the completeness checks. 
            html.Div: a table of the study data. 
            html.Div: radio buttons to select the time series for the scatterplot. 
            html.Div: a dropdown menu to select the variables to inspect. 
            dcc.Graph: a scatterplot of the selected variables.
            html.Div: a section containing alert messages if any variables go beyond its boundaries, guiding text to explain how to interpret out of bounds flags, and a summary statistics table for the selected variables.

        Returns html.Div containing an error message if the file format is not supported.
        Returns an empty string if no file is uploaded.

    Note:
        Updates global variables: df_relevant, df_believable, df_units, ds_time, and text when a valid file is successfully loaded.
        These are accessed by subsequent callbacks.
    
        The scatterplot, bounds alerts, and summary statistics table are initially populated with VolumetricFlowRate as the default variable.
        These update dynamically when the user selects different variables from the dropdown.
    """
    print('in first callback')
    if contents is not None:
        # Decode the uploaded file contents
        #print(f'contents: {contents}')
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file_content = io.StringIO(decoded.decode('utf-8'))
        raw_content = file_content.getvalue()
        file_content.seek(0)  # reset file pointer to the beginning
        print(
            f'file_content data type: {type(file_content)}, content: {file_content} and raw content: {raw_content}'
        )

        # load file as string
        #TODO: store text in a dcc.Store rather than a global variable, or consider another option for storing the raw text data that is accessible across callbacks without needing to reload the file or reprocess the text data multiple times.
        global text
        text = "\n".join([
            line for line in raw_content.splitlines() if line.strip() != ''
        ])  # remove empty lines
        file_content.seek(0)  # reset file pointer to the beginning
        #print(f'text data type: {type(text)} and content: {text}')

        # check to see if the file is in a format this program can analyze
        try:
            print('in big try, except block')
            # find start of table
            table_start = mf.find_table_start(text, '(HH:MM:SS)') + 1
            print(f'Table starts at row: {table_start}')
            '''# Preview the first few lines of the file to debug the structure
            preview_lines = mf.split_into_rows(text)[:10]
            print('Preview of the first 10 lines of the file:')
            for i, line in enumerate(preview_lines):
                print(f'Line {i}: {line}')
            '''
            '''
            # Print the lines after the table start row
            lines_after_start = mf.split_into_rows(text)[table_start:]
            print('Lines after the table start row:')
            for i, line in enumerate(lines_after_start[:10]):
                print(f'Line {i + table_start}: {line}')
            '''

            # Load the selected file as a DataFrame
            #file_content.seek(0)
            df = pd.read_csv(io.StringIO(text), skiprows=table_start)
            #df = pd.read_csv(file_content, skiprows=table_start)

            #close IO stream
            file_content.close()

            print(f'DataFrame shape: {df.shape}')
            print(f'DataFrame columns: {df.columns}')
            print(f'DataFrame head: {df.head()}')

            
            #TODO: use dcc.Store for df_relevant rather than global variable
            global df_relevant
            df_relevant = df.drop([
                'FLOWCTL', 'GPSRT', 'SD_DATAW', 'SD_HEADW', 'PumpPow1',
                'PumpPow2', 'SOC', 'PM1MCVar', 'PM2_5MCVar', 'PM4MCVar',
                'PM10MCVar', 'PM0_5NCVar', 'PM1NCVar', 'PM2_5NCVar',
                'PM4NCVar', 'PM10NCVar', 'PMtypicalParticleSizeVar',
                'AccelXVar', 'AccelYVar', 'AccelZVar', 'RotXVar', 'RotYVar',
                'RotZVar', 'BFGenergy'
            ],
                                  axis=1).round(1)

            # store a dataframe that contains the relevant variable names and their units of measurement
            #TODO: use dcc.Store for df_units rather than global variable
            global df_units
            df_units = pd.read_csv(
                io.StringIO(text),
                skiprows=table_start -
                1,  #units are listed in the row above the table start row
                header=None,
                nrows=3).reindex([1, 0]).transpose()
            df_units.columns = ['Variables', 'Units']
            df_units[
                'Names and Units'] = df_units['Variables'] + df_units['Units']
            print(
                f' UNITS DATAFRAME: {df_units.head(20)}, column names: {df_units.columns.to_list()}, unit columns exists: {df_units.Units}'
            )

            #TODO: use dcc.Store for df_believable rather than global variable
            global df_believable
            df_believable = df_relevant[[
                'UnixTime', 'SampleTime', 'DateTimeUTC', 'DateTimeLocal',
                'VolumetricFlowRate', 'AtmoT', 'PumpT', 'FdpT', 'BattT',
                'AccelT', 'AtmoP', 'PumpP', 'FdPdP', 'PumpRH', 'AtmoRho',
                'PumpV', 'MassFlow', 'BFGvolt', 'TPumpsON', 'TPumpsOFF'
            ]]

           #TODO: use dcc.Store for ds_time rather than global variable
            global ds_time
            ds_time = df_believable['UnixTime']
            #print(ds_time)

            # tuple that contains an alert message and dataframe showing the user how long a variables was below and above its boundaries.
            # initially populate with VolumetricFlowRate as the default variable, then update dynamically when the user selects different variables from the dropdown.
            bounds = mf.check_bounds(df_boundary_numbers,
                                     ['VolumetricFlowRate'], 'VARIABLE',
                                     df_believable, ds_time, ds_keywords,
                                     ds_replacements, text)
            df_bounds = bounds[
                1]  # the second part of the tuple, a pandas dataframe

            # initially populate with VolumetricFlowRate as the default variable, then update dynamically when the user selects different variables from the dropdown.
            df_stats = mf.summary_stats(df_believable, ['VolumetricFlowRate'],
                                        df_bounds, ds_keywords,
                                        ds_replacements)

            #print stuff to terminal to know better what is going on
            #print(mf.summary_stats(df_believable, ['VolumetricFlowRate'], df_bounds, ds_keywords, ds_replacements))

            return html.Div(
                id='file_info_container',
                children=[
                    html.Span('Showing results for file'),
                    html.Span(mf.pull_value(text, 'LogFilename')),
                    html.P(mf.on_load(text, ds_time),
                        style={'whiteSpace': 'pre-line'})
                ]
            ), html.Div(
                # return a table of the study data from the dataframe
                id='table1_container',
                children=[
                    html.H2(strings.title_table1),
                    dash_table.DataTable(
                        id='table1',
                        data=df_relevant.to_dict('records'),
                        columns=[{
                            'id': col, #tried this code to make it an index I could reference in selecting columns, preventing any data from displaying in table
                            'name': col,
                            #'selectable': True,
                            'hideable': True
                        } for idx, col in enumerate(df_relevant.columns)],
                        tooltip_header={i: df_dictionary['Description'][i] for i in df_relevant.columns},
                        virtualization=True,  #allows faster loading for large tables
                        #column_selectable = 'multi',
                        #selected_columns = [],
                        fixed_columns={
                            'headers': True,
                            'data': 1
                        },
                        fixed_rows={
                            'headers': True
                        },  #still see header names as scroll through table
                        style_cell={
                            'minWidth': 180,
                            'width': 180,
                            'maxWidth': 180
                        },  #set width to see header names, may use a wrap technique when names contain spaces
                        style_table={
                            'height': 350,  # default is 500
                            'minWidth': '100%'
                        },
                        style_header={
                            'backgroundColor': 'darkgrey',
                            'fontWeight': 'bold',
                        }),
                ]
            ), html.Div(  # return radio buttons to select desired time series for the x-axis of the scatterplot
                id='radio_items_container',
                children=[
                    html.P(strings.select1,
                        style={
                            'fontWeight': 'bold',
                            'display': 'inline'
                        }),
                    dcc.RadioItems(options=list(df_believable.columns.values[1:4]),
                                value='DateTimeLocal',
                                id='time-series-radio-buttons',
                                inline=True,
                                style={'display': 'inline'})
                ]
            ), html.Div(  # return a dropdown menu to select desired series to plot on the scatterplot and analyze
                id='dropdown_container',
                children=[
                    html.P(strings.select2,
                        style={
                            'fontWeight': 'bold',
                            'display': 'inline'
                        }),
                    dcc.Dropdown(options=list(df_believable.columns.values[4:]),
                                value=['VolumetricFlowRate'],  # initially populate with VolumetricFlowRate as the default variable, then update dynamically when the user selects different variables from the dropdown.
                                id='variable-dropdown',
                                multi=True,
                                placeholder='Select Sensor Data')
                ],
                style={
                    'display': 'inline',
                    'width': '50%',
                    'height': '40px'
                }
            ), dcc.Graph(  # return a scatterplot
                id='graph', figure={}
            ), html.Div(  # return a warning if data goes beyond a certain range
                id='Error-message-container',
                children=[
                    html.H2('Sensor Value Range'),
                    html.P(children=bounds[0],
                           id='error-message',
                           style={
                               'display': 'inline-block',
                               'width': '50%'
                           }),
                    # return guiding text to explain how to interpret out of bounds flags
                    html.Div(
                        [
                            html.H3('How to interpret out of range flags'),
                            html.P(strings.flags_guiding_text)
                        ],
                        style={
                            'display': 'inline-block',
                            'width': '50%',
                            'position': 'absolute'
                        }),
                    dcc.Store(id='bounds_store', data=bounds[1].to_dict('records'))
                ],
                style={
                    'whiteSpace': 'pre-line'
                }), html.Div(  # return summary statistics as a table #TODO: separate summary stats table into its own div for organization/layout purposes
                    id='stats-container',
                    children=[
                        html.H2('Summary Statistics'),
                        html.Div(
                            dash_table.DataTable(
                                id='stats',
                                data=df_stats.to_dict('records'),
                                columns=[{
                                    "name": i,
                                    "id": i
                                } for i in df_stats.columns],
                                hidden_columns=['beyondLimit'],  # hide column used for conditional styling 
                                tooltip_header={
                                    'Variable': 'Measured metric of interest',
                                    'Mean': strings.mean_explanation,
                                    'Standard Deviation': strings.stdDev_explanation,
                                    'Coefficient of Variation': strings.coefV_explanation,
                                    'Inter-Quartile Range': strings.iqr_explanation
                                },
                                style_as_list_view=
                                True,  #remove vertical lines in table
                                style_header={
                                    'backgroundColor': 'darkgrey',
                                    'fontWeight': 'bold'
                                },
                                style_data={ # wrap long content with spaces onto the next line
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                },
                                style_cell={
                                    'maxWidth': 100
                                },
                                style_header_conditional=[{
                                    'if': {
                                        'column_id': 'Variable',
                                    },
                                    'textAlign': 'left'
                                }],

                                style_data_conditional=[{
                                        'if': {
                                            'column_id': 'Variable',
                                        },
                                        'textAlign': 'left'
                                    }, {
                                        'if': {
                                            'row_index': 'odd'  # Temporary test to see if conditional styling works
                                        },
                                        'backgroundColor': 'lightgrey'
                                    }],
                            ),
                            style={
                                'width': '48%',
                                'display': 'inline-block'
                            }),
                        ])
        except ValueError as error:  #NameError?, ValueError?, EOFError?, RuntimeError?
            print('Program error:')
            print(traceback.format_exc())
            logging.error(traceback.format_exc())
            return html.Div(
                id='file-error',
                children=[
                    html.
                    P('File format is not supported. Program cannot read this file.'
                      ),
                    #html.P(error)
                ])
    else:
        return ""

# callback for selected columns in table1
@app.callback(
    Output(component_id='table1', component_property='fixed_columns'),
    Input(component_id='table1', component_property='selected_columns')
)
def pin_columns(selected_columns):
    print(f'SELECTED COLUMNS IN FIRST TABLE: {selected_columns}')
    if selected_columns:
        column_ids = [(col.get('id') * 1) for col in selected_columns]
        print(f'SELECTED COLUMN IDS: {column_ids} type: {type(column_ids)}')
        return {'headers': True, 'data': column_ids}
    else:
        return {'headers': True, 'data': 0}

# callback for scatterplot after selecting a time-series and certain variables
@app.callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='variable-dropdown', component_property='value'),
    Input(component_id='time-series-radio-buttons',
          component_property='value'))
def update_scatterplot(selected_variables, selected_time_series):
    print(f'SELECTED VARIABLES IN SCATTERPLOT CALLBACK {selected_variables}')
    return mf.update_scatterplot(df_believable, selected_variables,
                                 selected_time_series)


# Callback for alert function
@app.callback(
    Output(component_id='error-message', component_property='children'),
    Output(component_id='bounds_store', component_property='data'),
    Input(component_id='variable-dropdown', component_property='value'))
def check_bounds(selected_variables):
    bounds = mf.check_bounds(df_boundary_numbers, selected_variables,
                             'VARIABLE', df_believable, ds_time, ds_keywords,
                             ds_replacements, text)
    print(f'BOUNDS AFTER ALERT CALLBACK: {bounds}')
    return bounds[0], bounds[1].to_dict('records')


# Callback for summary statistics
@app.callback(
    Output(component_id='stats', component_property='data'),
    Output(component_id='stats', component_property='style_data_conditional'),
    Input(component_id='bounds_store', component_property='data'),
    Input(component_id='variable-dropdown', component_property='value')
    )
def summary_stats(bounds_data, selected_variables):
    bounds_df = pd.DataFrame(bounds_data)
    stats_df = mf.summary_stats(df_believable, selected_variables, bounds_df, ds_keywords, ds_replacements)
    style_data_conditional = [{
        'if': {
            'filter_query': '{beyondLimit} = True'
        },
        'backgroundColor': 'orange',
        'color': 'white'
    }]

    print(
        f'INSIDE STATS CALLBACK. SELECTED VARIABLES: {selected_variables}, MAIN DATAFRAME: {df_believable.columns}, BOUNDS DATAFRAME: {bounds_data}, STATS DATAFRAME: {stats_df}'
    )
    return stats_df.to_dict('records'), style_data_conditional


# run application
def run_dash():
    app.run(debug=True, use_reloader=False) #host='0.0.0.0', port=8099


if __name__ == "__main__":
    # Start Dash server in a separate thread
    dash_thread = threading.Thread(target=run_dash)
    dash_thread.start()
