from fastapi import FastAPI, Depends
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pi
import json
from fastapi.middleware.cors import CORSMiddleware
from ui_data_model import FilterItem, Path, ColorValue
from backend_schema import get_chart_values, get_chart_type
from utils.tracking import track_endpoint_usage
import os
import asyncio
from fastapi.responses import JSONResponse
from typing import Dict, Union, List
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import plotly.graph_objects as go
from dotenv import load_dotenv
import os 




load_dotenv()

DATA_FILEPATH = os.environ.get("DATA_FILEPATH")



##################
#### DATA #######
###################
global df 


df = pd.read_csv(DATA_FILEPATH)


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChartRequest(BaseModel):
    chart_type: Optional[str] = None
    value: Optional[List[str]] = None
    path: Optional[List[str]] = None
    filter: Optional[List[str]] = None
    colour: Optional[List[str]] = None
    msg: Optional[str] = None


###########################################
#### define list of values
###########################################

color_type_plot = [
    "ACV (Bookings)",
    "ACV YoY %",
    "Win Rate",
    "BUD Attain",
    "# of Accounts",
    "Avg Deal Size",
    "# of AEs",
    "ACV per AE",
    "# of Accounts per AE",
    "COPA (Revenue)",
    "REV YoY %",
    "Market YoY %",
    "Market Share %",
    "MS Changes (pp.)",
    "%Direct Rev Covered by CSPs",
    "%Private Bookings Covered by CAAs",
    "%Private Bookings Covered by PLs",
    "%Private Bookings Covered by CDMs",
]

region_type_plot = [
    "Region L1",
    "Region L2",
    "Region L3",
    "Region Country",
    "2022 Sub-Solution Area",
    "2022 Solution Area L3",
    "Channel",
    "Distribution Channel",
    "Industry Sector",
    "ISS",
    "IAC",
    "Deployment",
    "RISE Flag",
    "Material ID",
    "2023 Sub-Solution Area",
    "2023 Solution Area L3",
]

hover_data = [
    "ACV YoY %",
    "Win Rate",
    "BUD Attain",
    "# of Accounts",
    "Avg Deal Size",
    "# of AEs",
    "ACV per AE",
    "# of Accounts per AE",
    "COPA (Revenue)",
    "REV YoY %",
    "Market YoY %",
    "Market Share %",
    "MS Changes (pp.)",
    "%Direct Rev Covered by CSPs",
    "%Private Bookings Covered by CAAs",
    "%Private Bookings Covered by PLs",
    "%Private Bookings Covered by CDMs",
]

filter_data = [
    "North America","Europe","Asia","Africa","USA","UK", "France","Germany", "Italy", "Spain", "Japan", "South Korea", "China", "Thailand", "Australia", "Canada", "Russia", "India", 
    "Egypt","New York",
"Los Angeles",
"Chicago",
"Houston",
"Miami",
"London",
"Paris",
"Berlin",
"Rome",
"Madrid",
"Tokyo",
"Seoul",
"Beijing",
"Shanghai",
"Bangkok",
"Sydney",
"Melbourne",
"Toronto",
"Vancouver",
"Moscow",
"Mumbai",
"Cairo"]


###########################################
#### define plotting functions
###########################################
## stylised functions
def get_text_format(color_dimension):
    d = {
        "ACV (Bookings)": ".3s",
        "ACV YoY %": ".0%",
        "Win Rate": ".0%",
        "BUD Attain": ".0%",
        "# of Accounts": ".0f",
        "Avg Deal Size": ".3s",
        "# of AEs": ".0f",
        "ACV per AE": ".3s",
        "# of Accounts per AE": ".1f",
        "COPA (Revenue)": ".3s",
        "REV YoY %": ".0%",
        "Market YoY %": ".0%",
        "Market Share %": ".1%",
        "MS Changes (pp.)": ".1%",
        "%Direct Rev Covered by CSPs": ".0%",
        "%Private Bookings Covered by CAAs": ".0%",
        "%Private Bookings Covered by PLs": ".0%",
        "%Private Bookings Covered by CDMs": ".0%",
    }
    return d[color_dimension]


def get_color_range(color, agg_booking):
    color_ranges = {
        "ACV YoY %": [-0.2, 1],
        "Win Rate": [0, 0.5],
        "BUD Attain": [0.8, 1.2],
        "REV YoY %": [0, 0.5],
        "Market YoY %": [0, 0.5],
        "Market Share %": [0, 0.03],
        "%Direct Rev Covered by CSPs": [0.8, 1],
        "%Private Bookings Covered by CAAs": [0.8, 1],
        "%Private Bookings Covered by PLs": [0.8, 1],
        "%Private Bookings Covered by CDMs": [0.8, 1],
    }
    if color in color_ranges:
        return color_ranges[color]
    else:
        return [np.min(agg_booking[color]), np.max(agg_booking[color])]


def generate_tooltip(fig, value, hover_data, color):
    custom_data = fig.data[0].customdata
    hover_template = "<b>%{label}</b><br><b>" + value + "</b>: %{value:.3s}<br>"
    # last item of the customdata is color
    for i in range(0, custom_data.shape[1]):
        if i != custom_data.shape[1] - 1:
            hover_data_item = hover_data[i]
            hover_template += (
                "<b>"
                + hover_data_item
                + "</b>"
                + ": %{customdata["
                + str(i)
                + "]:"
                + get_text_format(hover_data_item)
                + "}"
            )
            hover_template += "<br>"
        else:
            hover_data_item = color
            hover_template += (
                "<b>"
                + hover_data_item
                + "</b>"
                + ": %{customdata["
                + str(i)
                + "]:"
                + get_text_format(hover_data_item)
                + "}"
            )
    return hover_template



def generate_box_text(fig, value, color):
    # only get the first item (box size) of the customdata
    # and the last item (color) of the customdata

    custom_data = fig.data[0].customdata
    text_template = (
        "<b>%{label}</b><br><b>"
        + color
        + "</b>: %{customdata["
        + str(custom_data.shape[1] - 1)
        + "]:"
        + get_text_format(color)
        + "}"
    )
    return text_template


### actual plotting functions

def draw_treemap(df, path, value, colour, filter):
    """function for drawing treemap
    Args:
      df: dataframe of the data to plot
      path: specified path/region to plot the data
      value: value to plot the data
    Returns:
        fig
    """
    # create a filter dictionary
    filter_dict = {}
    
    filter_dict["Region L1"] = [
        "North America","Europe","Asia","Africa"]


    filter_dict["Region L2"] = [
        "USA","UK", "France","Germany", "Italy", "Spain", "Japan", "South Korea", "China", "Thailand", "Australia", "Canada", "Russia", "India", "Egypt"]
    
    filter_dict["Region Country"] = [
        "USA","UK", "France","Germany", "Italy", "Spain", "Japan", "South Korea", "China", "Thailand", "Australia", "Canada", "Russia", "India", "Egypt"]

    filter_dict["Region L3"] = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Miami",
        "London",
        "Paris",
        "Berlin",
        "Rome",
        "Madrid",
        "Tokyo",
        "Seoul",
        "Beijing",
        "Shanghai",
        "Bangkok",
        "Sydney",
        "Melbourne",
        "Toronto",
        "Vancouver",
        "Moscow",
        "Mumbai",
        "Cairo"
    ]
    # filter_dict["Region Country"] = [
    #     "France",
    #     "Netherlands",
    #     "Norway",
    #     "United Kingdom",
    #     "Sweden",
    #     "Denmark",
    # ]

    filter_list = filter

    df_filter = ""

    # #just filter out the zeros from the df
    if type(filter_list) == list:
        if len(filter_list) != 0:
            for filter_value in filter_list:
                for key in filter_dict.keys():
                    if filter_value in filter_dict[key]:
                        filter_name = key

            df_filter = df[df[filter_name].isin(filter_list)].copy()
            print(f"ORIGINAL {df_filter}")
            df = df_filter[
                df_filter[value] > 0
            ]  # keep only the positive non-zero values
    else:
        df_filter = df.copy()
        print(f"ORIGINAL {df_filter}")
        df = df[df[value] > 0]  # keep only the positive non-zero values

    # for now we set color to the same as path
    if type(colour) == list:
        if len(colour) == 0:
            color = value
        else:
            color = colour[0]
    else:
        color = value

    fig = px.treemap(
        df,
        path=path,
        values=value,
        color=color if color is not None else "win_rate",
        hover_data=hover_data,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0.3,
        range_color=get_color_range(color, df)
        # color_continuous_midpoint=np.mean(agg_booking[color]),
        # range_color=[min(agg_booking[color]), max(agg_booking[color])]
    )
    hover_template = generate_tooltip(fig, value, hover_data, color)
    text_template = generate_box_text(fig, value, color)

    fig.data[0].texttemplate = text_template
    fig.data[0].textposition = "middle center"
    fig.data[0].textfont = {"size": 14}

    fig.update_traces(marker_line_width=2, hovertemplate=hover_template)

    return fig, df_filter

def draw_scatter(df, value_x, value_y, path):
    """function for drawing treemap

    Args:
      df: dataframe of the data to plot
      value_x: x-axis values to plot
      value_y: y-axis values to plot
      path: path/region of the data to plot

    Returns:
        fig
    """
    # for now we set color to the same as path

    fig = px.scatter(
        df,
        x=value_x,
        y=value_y,
        hover_data=path
        #  color_continuous_scale='RdYlGn',
        #  color_continuous_midpoint=0.3,
        #  range_color=get_color_range(color, df)
        # color_continuous_midpoint=np.mean(agg_booking[color]),
        # range_color=[min(agg_booking[color]), max(agg_booking[color])]
    )
    # hover_template = generate_tooltip(fig, value, hover_data, color)
    # text_template = generate_box_text(fig, value, color)
    
    
    layout = fig['layout']
    plot_bgcolor = layout['plot_bgcolor']
    x_max = max(fig.data[0].x)
    y_max = max(fig.data[0].y)

    #Title
    fig.update_layout(
        title={
            'text': f"Scatter Plot of <b>{value_x}</b> and <b>{value_y}</b> in <b>{path[0]}</b>",
            'x': 0.5,
            'y': 0.9,
            'xanchor': 'center',
            'yanchor': 'top',
        }
    )
    
    #Label
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.95,
        y=0.95,
        text=f"X-axis: {value_x}<br>Y-axis: {value_y}",
        showarrow=False,
        font=dict(size=12),
        bgcolor=plot_bgcolor,
        bordercolor='white',
        borderwidth=1,
        borderpad=5,
        xanchor='right',
        yanchor='top'
    )
    # fig.data[0].texttemplate = text_template
    # fig.data[0].textposition = 'middle center'
    # fig.data[0].textfont = {'size': 14}
    
    # fig.update_traces(marker_line_width=2, hovertemplate=hover_template)

    fig.update_traces(marker_size=10)

    return fig



def draw_bar(df, value, path):
    if len(value) == 1:
        fig = px.bar(
            df.sort_values(by=value[0], ascending=False),
            x=df[path[0]],
            y=df[value[0]],
        )
        return fig
    elif len(value) == 2:
        fig = go.Figure(
            data=[
                go.Bar(name=value[0], x=df[path[0]], y=df[value[0]]),
                go.Bar(name=value[1], x=df[path[0]], y=df[value[1]]),
            ]
        )
        return fig
    elif len(value) == 3:
        fig = go.Figure(
            data=[
                go.Bar(name=value[0], x=df[path[0]], y=df[value[0]]),
                go.Bar(name=value[1], x=df[path[0]], y=df[value[1]]),
                go.Bar(name=value[2], x=df[path[0]], y=df[value[2]]),
            ]
        )
        return fig



###########################################
#### fast api end points
###########################################


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/input")
async def process_input(user_input: str):
    chart_type = get_chart_type(user_input)
    return {
        "chart_type": chart_type,
        "chart_values": get_chart_values(user_input, chart_type),
    }


# pass in an input {chart_type: "tree", path: [path_val]}
# @app.post("/dataframe")
# async def get_data(user_input: Dict[str, Union[str, List[str]]]):
#     if "tree" in user_input["chart_type"]:
#         print(user_input["path"])
#         agg_df = data_computation.Consolidation(
#             group_var=user_input["path"], Y_filters={"Year": 2022}
#         )
#         print(agg_df.columns)
#         print(agg_df)
#         json_data = agg_df.to_json(orient="records")
#         return JSONResponse(content=json_data, media_type="application/json")


# Custom exception handler for HTTPException
@app.exception_handler(HTTPException)
async def handle_http_exception(request, exc):
    # Custom error response
    error_response = {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred",
    }
    return JSONResponse(status_code=exc.status_code, content=error_response)


@app.post("/parse_input")
async def parse_input(user_input: str):
    chart_dict = {}
    clean_chart_dict = {}
    value_list = []
    path_list = []
    colour_list = []
    filter_list = []
    msg = ""

    try:
        chart_type = get_chart_type(user_input)
        print(chart_type)
        ## input some error handling later here
        chart_dict["chart_type"] = chart_type
        chart_dict["chart_values"] = get_chart_values(user_input, chart_type)
        print(chart_dict)

        ## make sure it matches the column names for chart_type
        if "tree" in chart_type:
            clean_chart_dict["chart_type"] = "treemap"
            paths_keys = ["path1", "path2", "path3"]
        elif "line" in chart_type:
            clean_chart_dict["chart_type"] = "line"
        elif "scatter" in chart_type:
            clean_chart_dict["chart_type"] = "scatter"
        elif "bar" in chart_type:
            clean_chart_dict["chart_type"] = "bar"
        else:
            # default to treemap
            msg = msg + " Sorry, we cannot find a chart type, defaulting to treemap"
            clean_chart_dict["chart_type"] = "treemap"

        ## make sure it matches the column names for chart_values
        if (type(chart_dict["chart_values"]) == str) or (
            chart_dict["chart_values"] is None
        ):
            msg = msg + " No values found"
        ## we create a logic for parsing trees
        elif clean_chart_dict["chart_type"] == "treemap":
            chart_values = chart_dict["chart_values"]

            # check through values
            for value in color_type_plot:
                if value.lower() in chart_values["value"]:
                    value_list.append(value)

            # check through paths
            region_text = " ".join([chart_values[key] for key in paths_keys])
            for region in region_type_plot:
                if region.lower() in region_text:
                    path_list.append(region)

            # check through colour
            for colour in color_type_plot:
                if colour.lower() in chart_values["colour"]:
                    colour_list.append(colour)

            ##check through filter, note this is not lower case
            for actual_filter in filter_data:
                for filter in chart_values["filter"]:
                    if actual_filter.lower() == filter.lower():
                        filter_list.append(actual_filter)

            # special odd case for SL-FR-Industry 2
            if "SL-FR-Industry 2" in filter_list:
                filter_list.remove("SL-FR-Industry 2")
                filter_list.append("SL-FR- Industry 2")

        else:
            temp_list = [i for i in chart_dict["chart_values"].values()]
            temp_text = " ".join(temp_list)

            # check through values
            for value in color_type_plot:
                if value.lower() in temp_text:
                    value_list.append(value)

            # check through paths
            for region in region_type_plot:
                if region.lower() in temp_text:
                    path_list.append(region)

        ## input some default values if list is None?
        # handle emptypath list
        if len(path_list) == 0:
            msg = msg + " No region/path specified, defaulting to Region L1"
            path_list.append("Region L1")

        # handle empty values
        if len(value_list) == 0 and "tree" in clean_chart_dict["chart_type"]:
            msg = msg + " No values specified, defaulting to ACV booking"
            value_list.append("ACV (Bookings)")
        elif len(value_list) == 0 and "bar" in clean_chart_dict["chart_type"]:
            msg = msg + " No values specified, defaulting to ACV booking"
            value_list.append("ACV (Bookings)")
        elif len(value_list) == 0 and "line" in clean_chart_dict["chart_type"]:
            msg = msg + " no values specified, defaulting to ACV booking and revenue"
            value_list.append("ACV (Bookings)")
            value_list.append("COPA (Revenue)")
        elif len(value_list) == 0 and "scatter" in clean_chart_dict["chart_type"]:
            msg = msg + " no values specified, defaulting to ACV booking and revenue"
            value_list.append("ACV (Bookings)")
            value_list.append("COPA (Revenue)")

        # put everything into clean dictionary
        if "tree" in clean_chart_dict["chart_type"]:
            clean_chart_dict["value"] = value_list
            clean_chart_dict["path"] = path_list
            clean_chart_dict["colour"] = colour_list
            clean_chart_dict["filter"] = filter_list
            clean_chart_dict["msg"] = msg
        else:
            clean_chart_dict["value"] = value_list
            clean_chart_dict["path"] = path_list
            clean_chart_dict["msg"] = msg

        print("Printing...")
        print(clean_chart_dict)

        return clean_chart_dict
    except Exception as e:
        # Handle the exception
        error_response = {"error": "Internal Server Error", "detail": str(e)}

        print(e)
        clean_chart_dict["msg"] = msg + str(e)

        return clean_chart_dict


@app.post("/chart")
async def process_chart(request: ChartRequest):
    chart_type = request.chart_type
    value = request.value
    path = request.path
    msg = request.msg
    colour = request.colour
    filter = request.filter

    clean_chart_dict = {}

    clean_chart_dict["chart_type"] = chart_type
    clean_chart_dict["value"] = value
    clean_chart_dict["path"] = path
    clean_chart_dict["msg"] = msg
    clean_chart_dict["colour"] = colour
    clean_chart_dict["filter"] = filter

    global df

    try:
        # add on the fig in the dict
        if "tree" in clean_chart_dict["chart_type"]:
            fig, df_filter = draw_treemap(
                df=df,
                path=clean_chart_dict["path"],
                value=clean_chart_dict["value"][0],
                colour=clean_chart_dict["colour"],
                filter=clean_chart_dict["filter"],
            )
            clean_chart_dict["fig"] = json.loads(pi.to_json(fig))

            ## check if negative or zero values exist
            print(df_filter)
            list_cols = []
            if type(df_filter) != str:
                list_cols = df_filter[df_filter[clean_chart_dict["value"][0]] <= 0][
                    clean_chart_dict["path"][-1]
                ].tolist()
                if len(list_cols) > 0:
                    string_cols = ", ".join(list_cols)
                    msg_cols = f"The following values are not shown due to negative or zero values: {string_cols}"
                    clean_chart_dict["msg"] = msg + msg_cols
                    print(msg_cols)

        elif "scatter" in clean_chart_dict["chart_type"]:
            fig = draw_scatter(
                df=df,
                value_x=clean_chart_dict["value"][0],
                value_y=clean_chart_dict["value"][1],
                path=clean_chart_dict["path"],
            )
            clean_chart_dict["fig"] = json.loads(pi.to_json(fig))
        elif "bar" in clean_chart_dict["chart_type"]:
            fig = draw_bar(
                df=df, value=clean_chart_dict["value"], path=clean_chart_dict["path"]
            )
            clean_chart_dict["fig"] = json.loads(pi.to_json(fig))

        print(clean_chart_dict)
        return clean_chart_dict

    except Exception as e:
        # Handle the exception
        error_response = {"error": "Internal Server Error", "detail": str(e)}

        print(e)

        # prev_value = clean_chart_dict

        clean_chart_dict["msg"] = (
            str(e) + " Oops, an error occured. Returning default chart"
        )
        clean_chart_dict["chart_type"] = ["treemap"]
        clean_chart_dict["value"] = ["ACV (Bookings)"]
        clean_chart_dict["path"] = ["Region L1"]
        # clean_chart_dict['prev_values'] = prev_value

        # # Convert DataFrame to JSON serializable format
        # json_data = df.to_json(orient="records")
        # clean_chart_dict['data'] = json_data

        fig = draw_treemap(
            df=df,
            path=clean_chart_dict["path"],
            value=clean_chart_dict["value"][0],
            colour=clean_chart_dict["colour"],
            filter=clean_chart_dict["filter"],
        )
        clean_chart_dict["fig"] = json.loads(pi.to_json(fig))

        return clean_chart_dict

    #     # add on the fig in the dict
    #     if 'tree' in clean_chart_dict['chart_type']:
    #         fig = draw_treemap(df = df, path = clean_chart_dict['path'], value = clean_chart_dict['value'][0] )
    #         clean_chart_dict['fig']  = json.loads(pi.to_json(fig))
    #     elif 'scatter' in clean_chart_dict['chart_type']:
    #         fig = draw_scatter(df = df, value_x = clean_chart_dict['value'][0], value_y = clean_chart_dict['value'][1], path = clean_chart_dict['path'])
    #         clean_chart_dict['fig']  = json.loads(pi.to_json(fig))

    #     return clean_chart_dict

    # except Exception as e:
    #     # Handle the exception
    #     error_response = {
    #         "error": "Internal Server Error",
    #         "detail": str(e)
    #     }

    #     print(e)

    #     #prev_value = clean_chart_dict

    #     clean_chart_dict['msg'] = str(e) + ' Oops, an error occured. Returning default chart'
    #     clean_chart_dict['chart_type'] = ['treemap']
    #     clean_chart_dict['value'] = ['ACV (Bookings)']
    #     clean_chart_dict['path'] = ['Region L1']
    #     #clean_chart_dict['prev_values'] = prev_value

    #     df = data_computation.Consolidation(group_var=clean_chart_dict['path'] , Y_filters={'Year': 2022})

    #     # # Convert DataFrame to JSON serializable format
    #     # json_data = df.to_json(orient="records")
    #     # clean_chart_dict['data'] = json_data

    #     fig = draw_treemap(df = df, path = clean_chart_dict['path'], value = clean_chart_dict['value'][0] )
    #     clean_chart_dict['fig']  = json.loads(pi.to_json(fig))

    #     return clean_chart_dict
