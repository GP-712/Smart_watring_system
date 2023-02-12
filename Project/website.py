# Import necessary libraries
from sklearn.neighbors import KNeighborsClassifier
from datetime import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import sqlite3
import datetime
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import load_figure_template
import time
import threading

# define app
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.COSMO, dbc_css],
                meta_tags=[{"name": "viewport",
                            "content": "width=device-width"}],
                suppress_callback_exceptions=True)
load_figure_template("COSMO")


# create connect to database
db = sqlite3.connect('databases/messages.db')
cursor = db.cursor()
conn = sqlite3.connect('databases/pump.db')
cursor2 = conn.cursor()

# import data and create graph temp
dd = pd.read_sql_query(
    "SELECT (date || ' ' || time) as Times, AVG(temp) as Temperature  FROM messages WHERE Times >= strftime('%Y-%m-%d %H', datetime('now', '-1 day')) group by strftime ('%H',time) ORDER BY date(Times) asc",
    db)
FigTemp = px.line(dd, x='Times', y='Temperature', title='Average Temperatures')

# import data and create graph humid
dd = pd.read_sql_query(
    "SELECT (date || ' ' || time) as Times, AVG(humid) as Humidity FROM messages WHERE Times >= strftime('%Y-%m-%d %H', datetime('now', '-1 day')) group by strftime ('%H',time) ORDER BY date(Times) asc",
    db)
FigHumid = px.line(dd, x='Times', y='Humidity', title='Average Humidity')

# import data and create graph salt
#dd = pd.read_sql_query("SELECT AVG(salt) as Salinity , strftime ('%H',time) as Hour, date FROM messages WHERE   date >= datetime('now','-1 day') GROUP BY hour",db)
#FigSalt = px.line(dd, x='Hour', y='Salinity', title='Average Salinity')

# create table if not avaible and update category for all new sensors
cursor.execute(
    "CREATE TABLE IF NOT EXISTS sensors (device_name text, macAddress text, category text, UNIQUE(macAddress))")
cursor.execute(
    "INSERT OR IGNORE INTO sensors(macAddress) SELECT Min(device_name) AS device_name  FROM   messages GROUP BY device_name")
cursor.execute(
    "UPDATE sensors SET category = 'Not Selected' WHERE category IS NULL")
cursor.execute(
    "UPDATE sensors SET device_name = 'Not Selected' WHERE device_name IS NULL")
db.commit()
df = pd.read_sql_query(
    "SELECT Min(macAddress) AS macAddress, device_name, category FROM sensors GROUP BY macAddress", db)
dn = pd.read_sql_query(
    "SELECT strftime('%H',time) as hour , Min(device_name) AS device_name , date, strftime('%d-%m-%Y','now') as date_now, strftime('%H','now') as hour_now FROM messages WHERE (date = date_now AND hour<=hour_now) OR (date < date_now) GROUP BY device_name",
    db)
dz = pd.read_sql_query("SELECT Min(device_name) AS device_name, (date || ' ' || time) as Times, humid, temp, soil  FROM messages WHERE Times >= strftime('%Y-%m-%d %H', datetime('now', '-15 minutes')) GROUP BY device_name", db)
cursor2.execute(
    "CREATE TABLE IF NOT EXISTS controls (control_type TEXT, pump_state INTEGER, prediction INTEGER, datetimes TEXT)")
conn.commit()


dmlWasted = pd.read_sql_query("WITH pos_with_end(pump_state, prediction, datetimes, end) AS (SELECT pump_state, prediction, datetimes, lead(datetimes, 1, datetime(datetimes, 'start of year', '+1 year')) OVER (ORDER BY datetimes) FROM controls) SELECT datetimes as Times, round((strftime('%s', end) - strftime('%s', datetimes)) / 60.0, 0) AS 'wasted&needed water liter/min' FROM pos_with_end WHERE  pump_state==1 AND prediction==0 ", conn)
dmlNeeded = pd.read_sql_query("WITH pos_with_end(pump_state, prediction, datetimes, end) AS (SELECT pump_state, prediction, datetimes, lead(datetimes, 1, datetime(datetimes, 'start of year', '+1 year')) OVER (ORDER BY datetimes) FROM controls) SELECT datetimes as Times, (0 - round((strftime('%s', end) - strftime('%s', datetimes)) / 60.0, 0)) AS 'wasted&needed water liter/min' FROM pos_with_end WHERE  pump_state==0 AND prediction==1 ", conn)
dmlGood = pd.read_sql_query("SELECT datetimes as Times, (pump_state-prediction) AS 'wasted&needed water liter/min' FROM controls WHERE  pump_state == prediction", conn)
dmlAll = [dmlWasted, dmlNeeded, dmlGood]
resultDml = pd.concat(dmlAll)
resultDml = resultDml.sort_values(by="Times")
FigML = px.line(resultDml, x='Times', y='wasted&needed water liter/min', title='ML chart')
FigML.update_layout(hovermode="x unified")
type_control = 'null'

db.close()
conn.close()

# method check what last predict to change pump status


# function to predict the consumption currently it predicts the consumption .
# 0 stands for high consumption (stop the pump) 1 stands for low consumption (start the pump)
def predict():
    # load the training data
    df = pd.read_csv('labeled_dataset_soil-U.csv')

    # select the features and target for the model
    X = df[['salt', 'soil', 'temp', 'humid']]
    y = df['Gn']

    # create and train the KNN model
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X, y)

    # connect to the database
    conn = sqlite3.connect('databases/messages.db')

    # load the data

    test_data = pd.read_sql_query(
        "SELECT * FROM messages ORDER BY date desc , time DESC LIMIT 1", conn)
    # select the features from the external data
    conn.close()
    X_test = test_data[['salt', 'soil', 'temp', 'humid']]
    # predictions on the data
    predictions = knn.predict(X_test)
    return predictions[0]


# method get average for temp/humid/salt last 10 min


def get_record(mesure):
    db = sqlite3.connect('databases/messages.db')
    cursor = db.cursor()
    if (mesure == "temp"):
        cursor.execute(
            "SELECT ROUND(AVG(temp), 2) FROM messages WHERE (date || ' ' || time) >= strftime('%Y-%m-%d %H', datetime('now', '-10 minutes'))")
    elif (mesure == "soil"):
        cursor.execute(
            "SELECT ROUND(AVG(soil), 2) FROM messages WHERE (date || ' ' || time) >= strftime('%Y-%m-%d %H', datetime('now', '-10 minutes'))")
    elif (mesure == "humid"):
        cursor.execute(
            "SELECT ROUND(AVG(humid), 2) FROM messages WHERE (date || ' ' || time) >= strftime('%Y-%m-%d %H', datetime('now', '-10 minutes'))")
    else:
        db.close()
        return ("Nothing!")
    # cursor.execute(select_query,(mesure,))
    mesureN = cursor.fetchall()
    db.close()
    return (mesureN[0][0])


def ml_status(needed):
    conn = sqlite3.connect('databases/pump.db')
    cursor2 = conn.cursor()
    difference_time = cursor2.execute(
        "SELECT ROUND((JULIANDAY(datetime('now')) - JULIANDAY(datetimes)) * 24 * 60) AS difference FROM controls ORDER BY datetimes DESC LIMIT 1").fetchall()
    type_now = cursor2.execute(
        "SELECT control_type FROM controls ORDER BY datetimes DESC LIMIT 1").fetchall()
    pump_now = cursor2.execute(
        "SELECT pump_state FROM controls ORDER BY datetimes DESC LIMIT 1").fetchall()
    prediction_now = cursor2.execute(
        "SELECT prediction FROM controls ORDER BY datetimes DESC LIMIT 1").fetchall()
    conn.close()
    if needed == 'need':
        if type_now[0][0] == 'Auto':
            needed = 'Auto is work!'
        else:
            if pump_now == prediction_now:
                needed = 'you are good'
            else:
                if difference_time[0][0] > 0:
                    needed = f'farm wast {int(abs(difference_time[0][0]))} litters water'
                else:
                    needed = f'farm need {int(abs(difference_time[0][0]))} litters water'
    elif needed == 'advice':
        if type_now[0][0] == 'Auto':
            needed = 'No need for advice'
        else:
            if pump_now == prediction_now:
                needed = 'No need for advice'
            else:
                if difference_time[0][0] > 0:
                    needed = 'Turn off pump!'
                else:
                    needed = 'Turn on pump!'
    return needed


ml_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Current status", className="text-center")),
        dbc.CardBody([
            html.H5(ml_status('need'), className="text-center"),
        ]),
        dbc.CardFooter([
            html.H5(ml_status('advice'), className="text-center"),
        ]),
    ],
    color="secondary", inverse=True
)


# cards for average last 10 min


offc_humid = dbc.Button("Click here", color="light",
                        className="d-block mx-auto", id='button_humid'),\
    html.Div([
        dbc.Offcanvas(
            dash_table.DataTable(
                id='table-deviceName-humid',
                data=dz.to_dict('records'),
                columns=[
                    {'id': 'device_name', 'name': 'Device Name'},
                    {'id': 'Times', 'name': 'Time'},
                    {'id': 'humid', 'name': 'Humidity'},
                ],
                sort_action='native',
                style_as_list_view=True,
                style_cell={
                    'padding': '5px',
                    'textAlign': 'center'
                },
                style_header={
                    'color': '#2373cc',
                    'background': '#e9f2fc',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                },
            ),
            id="offc_humidy",
            scrollable=True,
            title="All humidity readings last 15 minutes",
            is_open=False,
        )])

humidity_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Humidity", className="text-center")),
        dbc.CardBody(
            [html.H2(str(get_record("humid")) + "%", className="text-center"), ]),
        dbc.CardFooter(offc_humid),
    ],
    color="primary", inverse=True
)


offc_soil = dbc.Button("Click here", color="light",
                       className="d-block mx-auto", id='button_salt'),\
    html.Div([
        dbc.Offcanvas(
            dash_table.DataTable(
                id='table-deviceName-soil',
                data=dz.to_dict('records'),
                columns=[
                    {'id': 'device_name', 'name': 'Device Name'},
                    {'id': 'Times', 'name': 'Time'},
                    {'id': 'soil', 'name': 'Soil moisture'},
                ],
                sort_action='native',
                style_as_list_view=True,
                style_cell={
                    'padding': '5px',
                    'textAlign': 'center'
                },
                style_header={
                    'color': '#2373cc',
                    'background': '#e9f2fc',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                },
            ),
            id="offc_soily",
            scrollable=True,
            title="All soil moisture readings last 15 minutes",
            is_open=False,
        )])

soil_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Soil Moisture", className="text-center")),
        dbc.CardBody([html.H2(str(get_record("soil")) +
                              "µS/cm", className="text-center"), ]),
        dbc.CardFooter(offc_soil),
    ],
    color="success", inverse=True
)


offc_temp = dbc.Button("Click here", color="light",
                       className="d-block mx-auto", id='button_temp'),\
    html.Div([
        dbc.Offcanvas(
            dash_table.DataTable(
                id='table-deviceName-temp',
                data=dz.to_dict('records'),
                columns=[
                    {'id': 'device_name', 'name': 'Device Name'},
                    {'id': 'Times', 'name': 'Time'},
                    {'id': 'temp', 'name': 'Temperature'},
                ],
                sort_action='native',
                style_as_list_view=True,
                style_cell={
                    'padding': '5px',
                    'textAlign': 'center'
                },
                style_header={
                    'color': '#2373cc',
                    'background': '#e9f2fc',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                },
            ),
            id="offc_temp-scrollable",
            scrollable=True,
            title="All temperature readings last 15 minutes",
            is_open=False,
        )])

temp_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Temperature", className="text-center")),
        dbc.CardBody(
            [html.H2(str(get_record("temp")) + "°C", className="text-center"), ]),
        dbc.CardFooter(offc_temp),
    ],
    color="danger", inverse=True
)

# define devices deactivated / update category devices / control water pump cards
deactivated_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Devices Deactivated",
                               className="text-center")),
        dbc.CardBody([
            dash_table.DataTable(
                id='devices-deactivated',
                data=dn.to_dict('records'),
                columns=[
                    {'id': 'device_name', 'name': 'Mac Address Devices'},
                ],
                style_cell={
                    'padding': '5px',
                    'textAlign': 'center'
                },
                style_header={
                    'color': '#2373cc',
                    'background': '#e9f2fc',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
            ),
        ]),
    ],
)

updateDevices_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Update Category Devices",
                               className="text-center")),
        dbc.CardBody([
            html.P("Select Device Name"),
            dcc.Dropdown(id='dd_deviceName',
                         options=[{'label': i, 'value': i}
                                  for i in df['macAddress'].unique()],
                         value='Not Selected', clearable=False),
            html.Br(),
            dcc.Input(id='input_deviceName', type='text',
                      placeholder='Name for the device'),
            html.Br(),
            html.Br(),
            html.P("Select Category"),
            dcc.Dropdown(id='dd_category', options=['Not Selected', 'Sikkry', 'Khalas'], value='Not Selected',
                         clearable=False, searchable=False),
            html.Br(),
            dcc.ConfirmDialog(
                id='confirm-danger',
                message='You want change catagory?',
            ),
            html.Div(id='dd-output-container')
        ]),
    ],
)

controlPump_card = dbc.Card(
    [
        dbc.CardHeader(html.H5("Control Pump", className="text-center")),
        dbc.CardBody([
            html.Label(['Choice control pump'], style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='pump-control',
                options=[
                    {'label': ' Auto', 'value': 'auto'},
                    {'label': ' ON', 'value': 'on'},
                    {'label': ' OFF', 'value': 'off'}
                ],
                value=type_control,
                labelStyle={'display': 'block'}
            )
        ]),
    ],
)


graphRow1 = dbc.Row([dbc.Col(id='ml_card', children=[ml_card]),
                     dbc.Col(id='humidity_card', children=[humidity_card]),
                     dbc.Col(id='temp_card', children=[temp_card]),
                     dbc.Col(id='soil_card', children=[soil_card]), ], justify="center")
graphRow2 = dbc.Row([dbc.Col(dcc.Graph(id="graphML", figure=FigML))])
graphRow3 = dbc.Row([dbc.Col(dcc.Graph(id="graphTemp", figure=FigTemp), md=6),
                     dbc.Col(dcc.Graph(id="graphHumid", figure=FigHumid), md=6)])
graphRow4 = dbc.Row([dbc.Col(id='deactivated_card', children=[deactivated_card]),
                     dbc.Col(id='updateDevices_card',
                             children=[updateDevices_card]),
                     dbc.Col(id='controlPump_card', children=[controlPump_card]), ], justify="center")
# define navbar
nav = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.Button(
            "Open Devices List",
            id="open-offcanvas-scrollable",
            n_clicks=0,
        )
        ),
        html.Div([dbc.Offcanvas(
            dash_table.DataTable(
                id='table-deviceName-category',
                data=df.to_dict('records'),
                columns=[
                    {'id': 'device_name', 'name': 'Device Name'},
                    {'id': 'macAddress', 'name': 'Mac Address'},
                    {'id': 'category', 'name': 'Category'},
                ],
                sort_action='native',
                style_as_list_view=True,
                style_cell={
                    'padding': '5px',
                    'textAlign': 'center'
                },
                style_header={
                    'color': '#2373cc',
                    'background': '#e9f2fc',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
            ),
            id="offcanvas-scrollable",
            scrollable=True,
            title="Devices List",
            is_open=False,
        )
        ])
    ],
    brand="Smart Watring System",
    color="black",
    dark=True
)

# define layout website
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav,
    html.Br(),
    graphRow1,
    html.Br(),
    graphRow2,
    html.Br(),
    graphRow3,
    html.Br(),
    graphRow4,
    html.Br(),
])


@app.callback(
    Output("offc_humidy", "is_open"),
    Input("button_humid", "n_clicks"),
    State("offc_humidy", "is_open"),
)
def toggle_offcanvas_Humid(n2, is_open):
    if n2:
        return not is_open
    return is_open


@app.callback(
    Output("offc_soily", "is_open"),
    Input("button_salt", "n_clicks"),
    State("offc_soily", "is_open"),
)
def toggle_offcanvas_Salt(n2, is_open):
    if n2:
        return not is_open
    return is_open


@app.callback(
    Output("offc_temp-scrollable", "is_open"),
    Input("button_temp", "n_clicks"),
    State("offc_temp-scrollable", "is_open"),
)
def toggle_offcanvas_Temp(n2, is_open):
    if n2:
        return not is_open
    return is_open


@app.callback(
    Output('pump-control', 'value'),
    [Input('pump-control', 'value')])
def record_control_data(valueControl):
    conn = sqlite3.connect('databases/pump.db')
    cursor = conn.cursor()
    result0 = cursor.execute(
        "SELECT control_type FROM controls ORDER BY datetimes DESC LIMIT 1").fetchall()
    result1 = cursor.execute(
        "SELECT pump_state FROM controls ORDER BY datetimes DESC LIMIT 1").fetchall()
    prediction = int(predict())
    rowCount = len(result0)
    if prediction == 0:
        predictionAuto = 1
    else:
        predictionAuto = 0
    if valueControl == 'auto':
        if rowCount == 0 or result0 != 'auto':
            cursor.execute("INSERT INTO controls (control_type, pump_state, prediction, datetimes) VALUES (?,?,?,?)",
                           ('Auto', prediction, prediction, datetime.datetime.now()))
            print("pump now it auto")
    elif valueControl == 'on' or valueControl == 'off':
        if valueControl == 'off' != result1:
            cursor.execute("INSERT INTO controls (control_type, pump_state, prediction, datetimes) VALUES (?,?,?,?)",
                           ('Manually', 0, prediction, datetime.datetime.now()))
            print("pump now is off")
        elif valueControl == 'on' != result1:
            cursor.execute("INSERT INTO controls (control_type, pump_state, prediction, datetimes) VALUES (?,?,?,?)",
                           ('Manually', 1, prediction, datetime.datetime.now()))
            print("pump now is on")

    conn.commit()

    # get the latest value from the controls table
    result2 = cursor.execute(
        "SELECT control_type FROM controls ORDER BY datetimes DESC LIMIT 1").fetchone()
    if result2[0] == 'Auto':
        type_control = 'auto'
    elif result2[0] == 'Manually':
        result3 = cursor.execute(
            "SELECT pump_state FROM controls ORDER BY datetimes DESC LIMIT 1").fetchone()
        if result3[0] == 1:
            type_control = 'on'
        else:
            type_control = 'off'
    else:
        type_control = 'null'
    conn.close()
    return type_control

# Automation function :


def automation(nullValue):
    df = pd.read_csv('labeled_dataset_soil-U.csv')

    # select the features and target for the model
    X = df[['salt', 'soil', 'temp', 'humid']]
    y = df['Gn']

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X, y)

    conn_messages = sqlite3.connect('databases/messages.db')

    conn_pump = sqlite3.connect('databases/pump.db')

    # fetch last record
    test_data = pd.read_sql_query(
        "SELECT * FROM messages ORDER BY date desc , time DESC LIMIT 1", conn_messages)

    X_test = test_data[['salt', 'soil', 'temp', 'humid']]

    # prediction 0 == turn the pump off , 1 turn the pump on
    # i had to use [0] to extract the result from the array . eaitehr this way or replace the if condetion below to if prediction[0] == etc .
    prediction = knn.predict(X_test)[0]
    print(prediction)# just for checing purposes

    # Check the last state of the pump
    last_control = pd.read_sql_query(
        "SELECT * FROM controls ORDER BY datetimes desc  LIMIT 1", conn_pump)

    if last_control.iloc[0]['control_type'] == 'Auto':
        if prediction == 0:
            conn_pump.execute(
                "INSERT INTO controls (control_type, pump_state,datetimes) VALUES (?,?,?)", ('Auto', 'off', datetime.datetime.now()))
        else:
            conn_pump.execute(
                "INSERT INTO controls (control_type, pump_state,datetimes) VALUES (?,?,?)", ('Auto', 'on', datetime.datetime.now()))

    # Save changes
    conn_pump.commit()


# To run automation every 10 minutes
def job():
    while(True):
        automation("null")
        time.sleep(600)

t = threading.Thread(target=job)
t.start()

# for device list


@app.callback(
    Output("offcanvas-scrollable", "is_open"),
    Input("open-offcanvas-scrollable", "n_clicks"),
    State("offcanvas-scrollable", "is_open"),
)
def toggle_offcanvas_scrollable(n1, is_open):
    if n1:
        return not is_open
    return is_open


# for confirm change category
@app.callback(
    Output('confirm-danger', 'displayed'),
    Input('dd_category', 'value'),
    Input('dd_deviceName', 'value')
)
def display_confirm(valueCategory, valueDeviceName):
    if valueDeviceName != 'Not Selected':  # for confirm select device
        if valueCategory != 'Not Selected':  # for confirm select category
            return True
        return False
    return False


# for change category
@app.callback(
    Output('dd-output-container', 'children'),
    Input('dd_deviceName', 'value'),
    Input('input_deviceName', 'value'),
    Input('dd_category', 'value'),
    Input('confirm-danger', 'submit_n_clicks')
)
def update_output(valueName, valueInName, valueCate, submit_n_clicks):
    if valueInName:
        if submit_n_clicks:
            db = sqlite3.connect('databases/messages.db')
            cursor = db.cursor()
            cursor.execute(
                '''UPDATE sensors SET category = ?, device_name = ? WHERE macAddress = ?''', (valueCate, valueInName, valueName,))
            db.commit()
            db.close()
            return f'You have select category {valueCate} for device {valueName}'


# Run the app on all port server
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='80', debug=True)
