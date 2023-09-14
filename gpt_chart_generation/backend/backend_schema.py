#!/usr/bin/env python
# coding: utf-8

# In[1]:


from langchain.chat_models import AzureChatOpenAI
from kor import Object, Text
from kor.extraction import create_extraction_chain
from langchain.prompts import PromptTemplate
import openai
import plotly.express as px
import pandas as pd
import json
import re
import requests
from dotenv import load_dotenv
import os 
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

llm3 = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    max_tokens=2000,
    frequency_penalty=0,
    presence_penalty=0,
    top_p=1.0,
)

region_type = [
    "Region L1 - BM",
    "Region L2 - B",
    "Region L3",
    "Region Country -M",
    "2022 Sub-Solution Area - BM",
    "2022 Solution Area L3",
    "Channel",
    "Distribution Channel",
    "Industry Sector - M",
    "Industry Sector - M",
    "ISS",
    "IAC",
    "S/4 Deployment",
    "RISE Flag",
    "Material ID",
    "2023 Sub-Solution Area",
    "2023 Solution Area L3",
]
region_type = list(map(str.lower, region_type))

color_type = [
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
color_type = list(map(str.lower, color_type))


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

# ### Handling backend logic

# #### check chart type

# In[2]:


## chart_type

chart_type_schema = Object(
    id="chart",
    # Description of what your object is about
    description="Type of the chart in the sentence",
    # Fields that you would like to extract w.r.t your object
    attributes=[
        Text(
            id="chart_type",
            description="The type of chart shown in the sentence, \
                                                    the returned text should be one of those words in the CHART_LIST below\
                                                    CHART_LIST:{chart_type},\
                                                    typo may appear in the sentence,\
                                                    if the keyword selected does not exist in the CHART_LIST above, \
                                                    return the value in the CHART_LIST which is most similar to the one in the sentence",
            examples=[
                ("treeplot of region l3 s winrate, revenue", "tree"),
                ("plot", "plot"),
            ],
        )
    ],
    many=False,
)

chart_type_chain = create_extraction_chain(llm3, chart_type_schema)
chart_list = ["treemap", "scatter", "line", "bar"]


# #### handling line scatter logic

# In[3]:


line_scatter_schema = Object(
    id="chart",
    description="extract information to create a line chart ",
    attributes=[
        Text(
            id="yaxis",
            description="extract the yaxis columns",
            examples=[
                (
                    "plot a line chart of annual contract value bookings and deal size",
                    "annual contract value bookings",
                ),
            ],
        ),
        Text(
            id="xaxis",
            description="extract the xaxis columns",
            examples=[
                (
                    "plot a line chart of annual contract value bookings and deal size",
                    "deal size",
                ),
            ],
        ),
        Text(
            id="path",
            description='The "region" attribute of the data shown in the sentence,\
                        the returned text should be one of those words in the REGION_LIST below\
                        REGION_LIST:{region_type},\
                        typo may appear in the sentence,\
                        if the keyword selected does not exist in the REGION_LIST above, \
                        return the value in the REGION_LIST which is most similar to the one in the sentence,',
            examples=[
                ("scatter plot of region l1, acv and winrate", "region l1 - bm"),
            ],
        ),
        Text(
            id="chart",
            description="extract the type of chart",
            examples=[
                (
                    "plot a line chart of annual contract value bookings and deal size",
                    "line chart",
                ),
            ],
        ),
    ],
    examples=[
        (
            """
                scatter plot of win rate and deal size 
                """,
            [
                {
                    "yaxis": "win rate",
                    "xaxis": "deal size",
                    "chart": "scatter plot",
                    "path": "",
                },
            ],
        ),
        (
            """
                scatter plot of acv bookings and win rate by country 
                """,
            [
                {
                    "yaxis": "acv bookings",
                    "xaxis": "win rate",
                    "chart": "scatter plot",
                    "path": "country",
                },
            ],
        ),
        (
            """
                scatter plot of acv bookings and % private bookings covered by CAAs in region l2
                """,
            [
                {
                    "yaxis": "acv bookings",
                    "xaxis": "% private bookings covered by CAAs",
                    "chart": "scatter plot",
                    "path": "region l2",
                },
            ],
        ),
        (
            """
                scatter plot of acv bookings and % private bookings covered by CAAs
                """,
            [
                {
                    "yaxis": "acv bookings",
                    "xaxis": "% private bookings covered by CAAs",
                    "chart": "scatter plot",
                    "path": "",
                },
            ],
        ),
    ],
    many=False,
)
line_scatter_chain = create_extraction_chain(llm3, line_scatter_schema)


# ### Treemap

# In[4]:


treemap_schema = Object(
    id="chart",
    description="extract information to create a treemap chart",
    attributes=[
        Text(
            id="value",
            description="extract the value to plot the treemap chart",
            examples=[
                (
                    "plot a treemap chart of the winrate in region l2 and region l3 ",
                    "winrate",
                ),
                ("treemap of revenue and win rate ", "revenue"),
                (
                    "plot a treeplot of acv bookings in  with colour of revenue",
                    "acv bookings",
                ),
                (
                    "plot a treeplot of bookings with colour of revenue",
                    "bookings",
                ),
                (
                    "plot a treeplot of bookings in region l3",
                    "bookings",
                ),
            ],
        ),
        Text(
            id="path1",
            description="extract the first path to plot the treemap chart",
            examples=[
                (
                    "plot a treemap chart of the winrate in region l2 and region l3 ",
                    "region l2",
                ),
            ],
        ),
        Text(
            id="path2",
            description="extract the second path to plot the treemap chart",
            examples=[
                (
                    "plot a treemap chart of the winrate in region l2 and region l3 ",
                    "region l3",
                ),
            ],
        ),
        Text(
            id="path3",
            description="extract the third path to plot the treemap chart",
            examples=[
                (
                    "plot a treemap chart of the winrate in region l2 and region l3 and by industry sector",
                    "industry sector",
                ),
            ],
        ),
        Text(
            id="colour_value",
            description="extract the value if colour attribute is present",
            examples=[
                (
                    "plot a treemap chart of the winrate in region l2 and region l3, set colour to be win rate",
                    "win rate",
                ),
                (
                    "plot a treeplot of acv bookings in  with colour of revenue",
                    "revenue",
                ),
            ],
        ),
    ],
    examples=[
        (
            """
                plot a treemap chart of the winrate in region l2 and region l3 and by industry sector 
                """,
            [
                {
                    "value": "winrate",
                    "path1": "region l2",
                    "path2": "region l3",
                    "path3": "industry sector",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                plot a map of the revenue by sectors in region l2 
                """,
            [
                {
                    "value": "revenue",
                    "path1": "sectors",
                    "path2": "region l2",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treemap of the revenue in region l2 
                """,
            [
                {
                    "value": "revenue",
                    "path1": "region l2",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                tree plot of booking in region l2 
                """,
            [
                {
                    "value": "booking",
                    "path1": "region l2",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                tree map of revenue in region l2, region l3
                """,
            [
                {
                    "value": "revenue",
                    "path1": "region l2",
                    "path2": "region l3",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treeplot, regionl1, acv booking
                """,
            [
                {
                    "value": "acv booking",
                    "path1": "regionl1",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treeplot, region l2, revenue
                """,
            [
                {
                    "value": "revenue",
                    "path1": "region l2",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treeplot, revenue, region country 
                """,
            [
                {
                    "value": "revenue",
                    "path1": "region country",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                plot a treeplot in region l3 of avgdealsize
                """,
            [
                {
                    "value": "avgdealsize",
                    "path1": "region l3",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treemap of revenue and win rate
                """,
            [
                {
                    "value": "revenue",
                    "path1": "",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treemap of revenue by different countries
                """,
            [
                {
                    "value": "revenue",
                    "path1": "countries",
                    "path2": "",
                    "path3": "",
                    "colour_value": "",
                },
            ],
        ),
        (
            """
                treemap of revenue by different countries, colour is acv bookings
                """,
            [
                {
                    "value": "revenue",
                    "path1": "countries",
                    "path2": "",
                    "path3": "",
                    "colour_value": "acv bookings",
                },
            ],
        ),
        (
            """
                plot a treeplot of bookings with colour of revenue
                """,
            [
                {
                    "value": "bookings",
                    "path1": "",
                    "path2": "",
                    "path3": "",
                    "colour_value": "revenue",
                },
            ],
        ),
    ],
    many=False,
)
treemap_chain = create_extraction_chain(llm3, treemap_schema)


#### Bar chart schema
barchart_schema = Object(
    id="chart",
    description="extract information to create a barchart",
    attributes=[
        Text(
            id="value1",
            description="extract the first value to plot a bar chart",
            examples=[
                ("plot a bar chart of the winrate in region l2", "winrate"),
                (
                    "plot a bar chart of the acv booking and acv revenue in region l3",
                    "acv booking",
                ),
            ],
        ),
        Text(
            id="value2",
            description="extract the second value to plot a bar chart",
            examples=[
                (
                    "plot a bar chart of the acv booking and acv revenue in region l3",
                    "acv revenue",
                ),
            ],
        ),
        Text(
            id="value3",
            description="extract the third value to plot a bar chart",
            examples=[
                (
                    "plot a bar chart of the acv booking and acv revenue and win rate in region l3",
                    "win rate",
                ),
            ],
        ),
        Text(
            id="path",
            description="extract the path to plot the treemap chart",
            examples=[
                ("plot a barchart of the winrate in region l2", "region l2"),
            ],
        ),
    ],
    examples=[
        (
            """
                plot a bar chart of booking in region country 
                """,
            [
                {
                    "value1": "booking",
                    "value2": "",
                    "value3": "",
                    "path": "region country",
                },
            ],
        ),
        (
            """
                plot a bar chart of acv yoy%, rev yoy%, market yoy% in region country 
                """,
            [
                {
                    "value1": "acv yoy%",
                    "value2": "rev yoy%",
                    "value3": "market yoy%",
                    "path": "region country",
                },
            ],
        ),
    ],
    many=False,
)
barchart_chain = create_extraction_chain(llm3, barchart_schema)


# ### Handle multiple fuzzy match input

# In[5]:


# Fuzzy Matching Instruction Template and Schema
instruction_template = PromptTemplate(
    input_variables=["format_instructions", "type_description"],
    template=(
        """Your main task is to find the matching plot elements by doing a fuzzy match based on spelling between the user provided input column name and the list of actual column names. The match should ONLY be based on closest spelling ONLY. 
             When extracting the column name from the list, please make sure it matches the column name in the list exactly. Do not add any attributes that do not appear in the schema shown below.\n\n"""
        # "Add some type description\n\n"
        "{type_description}\n\n"  # Can comment out
        # "Add some format instructions\n\n"
        "{format_instructions}\n"
        # "Suffix heren\n"
    ),
)


# #### Line scatter match

# In[10]:


# ## Handle match

# line_scatter_match_schema = Object(
#     id="chart_match",
#     description="extract the matching information in the list",
#     attributes=[
#         Text(
#             id="yaxis",
#             description="extract the exact matching yaxis columns from the val_col list",
#             examples=[
#                 ("""input: {'yaxis': 'ACV booking', 'xaxis': 'revenue', 'path': 'region l2', 'chart': 'line chart'}
#                  val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']"""
#                  , "acv (bookings)"),
#                  ("""input: {'yaxis': 'private booking by caas', 'xaxis': 'revenue', 'path': 'region l2', 'chart': 'line chart'}
#                  val_col: ['%direct rev covered by csps','%private bookings covered by caas', '%private bookings covered by pls', '%private bookings covered by cdms']"""
#                  , "%private bookings covered by caas"),
#                     ("""input: {'yaxis': 'market share changes', 'xaxis': 'acv bookings', 'path': '', 'chart': 'scatter plot'}
#                  val_col: ['rev yoy %', 'market yoy %', 'market share %', 'ms changes (pp.)']"""
#                  , "ms changes (pp.)"),
#                       ],
#         ),
#         Text(
#             id="xaxis",
#             description="extract the exact matching xaxis columns from the val_col list",
#             examples=[
#                 ("""input: {'yaxis': 'ACV booking', 'xaxis': 'revenue', 'path': 'region l2', 'chart': 'line chart'}
#                  val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']"""
#                  , "copa (revenue)"),
#                       ],
#         ),
#         Text(
#             id='path',
#             description='extract the exact matching path from the path list',
#             examples=[
#                 ("""input: {'yaxis': 'ACV booking', 'xaxis': 'revenue %', 'path': 'region l2', 'chart': 'line chart'}
#                  path_col: ['region l1 - bm','region l2 - b','region l3']"""
#                  , "region l2 - b"),
#                 ("""input: {'yaxis': 'ACV booking', 'xaxis': 'revenue %', 'path': 'country', 'chart': 'line chart'}
#                  path_col: ['region l1 - bm','region l2 - b','region l3', 'region country']"""
#                  , "region country"),
#                       ],
#         ),
#     ],examples=[
#                         (
#                 """
#                 {'yaxis': 'ACV booking', 'xaxis': 'revenue %', 'path': 'region l2', 'chart': 'line chart'}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %']
#                 path_col: ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "yaxis": 'acv (bookings)', 'xaxis':'rev yoy %', 'path': 'region l2 - b'},
#                 ],
#             ),
#                                     (
#                 """
#                 {'yaxis': 'ACV booking', 'xaxis': 'revenue', 'path': 'region l2', 'chart': 'line chart'}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col: ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "yaxis": 'acv (bookings)', 'xaxis':'copa (revenue)', 'path': 'region l2 - b'},
#                 ],
#             ),
#             (
#                 """
#                 {'yaxis': 'bookings', 'xaxis': 'region l2, region l3', 'path': 'region l2', 'chart': 'scatter plot'}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col: ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "yaxis": 'acv (bookings)', 'xaxis':'', 'path': 'region l2 - b'},
#                 ],
#             ),
#             (
#                 """
#                 {'yaxis': 'number of aes', 'xaxis': 'revenue growth', 'path': 'country', 'chart': 'scatter plot'}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)', '# of aes']
#                 path_col: ['region l1 - bm','region l2 - b','region l3', 'region country']
#                 """,
#                 [
#                     { "yaxis": '# of aes', 'xaxis':'rev yoy %', 'path': 'region country'},
#                 ],
#             ),

#     ],many=False,
# )
# line_scatter_match  = create_extraction_chain(llm3, line_scatter_match_schema, instruction_template=instruction_template)


# # ##### treemap match

# # In[7]:


# ## Handle match

# treemap_match_schema = Object(
#     id="chart_match",
#     description="extract the matching information in the list",
#     attributes=[
#         Text(
#             id="value",
#             description="extract the exact matching value column from the val_col list",
#             examples=[
#                 ("""input: {'value': 'bookings', 'path1': 'region l2', 'path2': '', 'path3': 'industry sector'}
#                  val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %']"""
#                  , "acv (bookings)"),
#                 ("""input: {'value': 'win rate', 'path1': 'region l1', 'path2': '', 'path3': ''}
#                  val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %']"""
#                  , "win rate"),
#                  ("""input: {'value': 'revenue', 'path1': 'region l1', 'path2': '', 'path3': ''}
#                  val_col: ['copa (revenue)','acv yoy %', 'win rate', 'rev yoy %']"""
#                  , "copa (revenue)"),
#                       ],
#         ),
#         Text(
#             id="path1",
#             description="extract the exact matching path1 column from the path_col list",
#             examples=[
#                 ("""input: {'value': 'acv bookings', 'path1': 'region l2', 'path2': '', 'path3': 'industry sector'}
#                  path_col: ['region l1 - bm','region l2 - b','region l3', 'industry sector - m']"""
#                  , "region l2 - b"),
#                       ],
#         ),
#         Text(
#             id="path2",
#             description="extract the exact matching path2 column from the path_col list",
#             examples=[
#                 ("""input: {'value': 'acv bookings', 'path1': 'region l2', 'path2': '', 'path3': 'industry sector'}
#                  path_col: ['region l1 - bm','region l2 - b','region l3', 'industry sector - m']"""
#                  , "N\A"),
#                       ],
#         ),
#         Text(
#             id="path3",
#             description="extract the exact matching path3 column from the path_col list",
#             examples=[
#                 ("""input: {'value': 'acv bookings', 'path1': 'region l2', 'path2': '', 'path3': 'industry sector'}
#                  path_col: ['region l1 - bm','region l2 - b','region l3', 'industry sector - m']"""
#                  , "industry sector - m"),
#                       ],
#         ),
#     ],examples=[
#                         (
#                 """
#                 {'value': 'bookings', 'path1': 'region l2', 'path2': '', 'path3': 'industry sector'}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %']
#                 path_col: ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'acv (bookings)', 'path1':'region l2 - b', 'path2': 'N\A', 'path3': "industry sector - m" },
#                 ],
#             ),
#             (
#                 """
#                 {'value': 'number of accounts per ae', 'path1': 'region l2', 'path2': 'country', 'path3': 'channel'}
#                 val_col:  ['# of accounts','avg deal size','# of aes']
#                 path_col:  ['region l2 - b','region country -m','2022 sub-solution area - bm','2022 solution area l3','channel']
#                 """,
#                 [
#                     { "value": '# of aes', 'path1':'region l2 - b', 'path2': 'region country -m', 'path3': "channel" },
#                 ],
#             ),
#                         (
#                 """
#                 {'value': 'acv bookings', 'path1': 'region l2', 'path2': 'region l3', 'path3': ''}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col:  ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'acv (bookings)', 'path1':'region l2 - b', 'path2': 'region l3', 'path3': "" },
#                 ],
#             ),
#              (
#                 """
#                 {'value': 'revenue', 'path1': 'region l2', 'path2': '', 'path3': ''}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col:  ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'copa (revenue)', 'path1':'region l2 - b', 'path2': '', 'path3': "" },
#                 ],
#             ),
#                          (
#                 """
#                 {'value': 'copa revenue', 'path1': 'region l1', 'path2': '', 'path3': ''}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col:  ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'copa (revenue)', 'path1':'region l1 - bm', 'path2': '', 'path3': "" },
#                 ],
#             ),

#             (
#                 """
#                 {'value': 'win rate', 'path1': 'region l2', 'path2': '', 'path3': ''}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col:  ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'win rate', 'path1':'region l2 - b', 'path2': '', 'path3': "" },
#                 ],
#             ),
#              (
#                 """
#                 {'value': 'winrate', 'path1': 'regionl1', 'path2': '', 'path3': ''}
#                 val_col: ['acv (bookings)','acv yoy %', 'win rate', 'rev yoy %', 'copa (revenue)']
#                 path_col:  ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'win rate', 'path1':'region l1 - bm', 'path2': '', 'path3': "" },
#                 ],
#             ),
#             (
#                 """
#                 {'value': 'avg deal size', 'path1': 'region l2', 'path2': '', 'path3': ''}
#                 val_col: ['bud attain', '# of accounts', 'avg deal size']
#                 path_col:  ['region l1 - bm','region l2 - b','region l3']
#                 """,
#                 [
#                     { "value": 'avg deal size', 'path1':'region l2 - b', 'path2': '', 'path3': "" },
#                 ],
#             ),

#     ],many=False,
# )
# #line_scatter_chain  = create_extraction_chain(llm3, line_scatter_schema)
# treemap_match  = create_extraction_chain(llm3, treemap_match_schema, instruction_template=instruction_template)


# ### Handling overall logic

# In[20]:


#### USING GENERIC PROMPT ###############
# def generate_response(text):
#     response = openai.Completion.create(
#         engine=model_engine,
#         prompt=text,
#         temperature=0,
#         top_p=0,
#         max_tokens=500,
#         stop=None,
#         stream=False,
#     )
#     return response.choices[0].text.strip()


def generate_response(text):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    # Define the request payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": text}],
        "temperature": 0.7
    }

    # Make the API request
    response = requests.post(url, headers=headers, json=payload)

    # Process the response
    if response.status_code == 200:
        response_data = response.json()
        completed_message = response_data['choices'][0]['message']['content']
        return(completed_message)
    else:
        return(f"API request failed with status code {response.status_code}: {response.text}")


# base prompt for line & scatter
base_prompt_line_scatter = """Based on the dictionary below, do a fuzzy match based on the list of values and path, and provide the 
closest match in the list. Do not input your own values. 
- value = ['acv (bookings),acv yoy %,win rate,bud attain,# of accounts,avg deal size,# of aes,acv per ae,# of accounts per ae,copa (revenue),rev yoy %,market yoy %,market share %,ms changes (pp.),%direct rev covered by csps,%private bookings covered by caas,%private bookings covered by pls,%private bookings covered by cdms']
- path =  ['Region L1 - BM','Region L2 - B','Region L3','Region Country -M','2022 Sub-Solution Area - BM',\
    '2022 Solution Area L3','Channel','Distribution Channel','Industry Sector - M','Industry Sector - M',\
    'ISS','IAC','S/4 Deployment','RISE Flag','Material ID','2023 Sub-Solution Area','2023 Solution Area L3']

Format the output in json with the following keys, just return the json output do not include additional words:
- value1 - closest match based on the value list
- value2 - closest match based on the value list
- path - closest match based on the path list 

Input below:
"""


#########################
#### functions
def get_chart_type(user_input):
    chart_type = ""
    chart_type_output = chart_type_chain.predict_and_parse(
        text=f"user_input:{user_input}, chart_type_list:{chart_list}"
    )["data"]["chart"]
    if len(chart_type_output) != 0:
        chart_type = chart_type_output[0]["chart_type"]
        return chart_type
    else:
        chart_type = "unable to find plot"
        return chart_type


def output_match(parsed_dict, prompt):
    parsed_str = f"{parsed_dict}"
    line_scatter_prompt = f"""
    Based on the dictionary input below, do a fuzzy match based on the list of values and path, and provide the closest match in the list. Do not input your own values.
    - value = ['acv (bookings),acv yoy %,win rate,bud attain,# of accounts,avg deal size,# of aes,acv per ae,# of accounts per ae,copa (revenue),rev yoy %,market yoy %,market share %,ms changes (pp.),%direct rev covered by csps,%private bookings covered by caas,%private bookings covered by pls,%private bookings covered by cdms']
    - path =  ['region l1 - bm', 'region l2 - b', 'region l3', 'region country -m', '2022 sub-solution area - bm', '2022 solution area l3', 'channel', 'distribution channel', 'industry sector - m', 'industry sector - m', 'iss', 'iac', 's/4 deployment', 'rise flag', 'material id', '2023 sub-solution area', '2023 solution area l3']

    Format the output in json with the following keys, just return the json output do not include additional words:
    - value1 - closest match based on the value list
    - value2 - closest match based on the value list
    - path - closest match based on the path list

    Input below:
    {parsed_str}
    """
    tree_prompt = f""" 
    Based on the input dictionary below, do a fuzzy match based on the list of values and path, and provide the closest match in the list. Do not input your own values. 
    - value = ['acv (bookings),acv yoy %,win rate,bud attain,# of accounts,avg deal size,# of aes,acv per ae,# of accounts per ae,copa (revenue),rev yoy %,market yoy %,market share %,ms changes (pp.),%direct rev covered by csps,%private bookings covered by caas,%private bookings covered by pls,%private bookings covered by cdms']
    - path =  ['region l1 - bm', 'region l2 - b', 'region l3', 'region country -m', '2022 sub-solution area - bm', '2022 solution area l3', 'channel', 'distribution channel', 'industry sector - m', 'industry sector - m', 'iss', 'iac', 's/4 deployment', 'rise flag', 'material id', '2023 sub-solution area', '2023 solution area l3']

    Format the output in json with the following keys, just return the json output do not include additional words:
    - value - closest match based on the value list
    - path1 - closest match based on the path list 
    - path2 - closest match based on the path list 
    - path3 - closest match based on the path list 
    - colour_value - closest match based on the value list 

    Input below:
    {parsed_str}
    """

    # select prompts
    if prompt == "line_scatter_prompt":
        final_prompt = line_scatter_prompt
    elif prompt == "tree_prompt":
        final_prompt = tree_prompt

    print(final_prompt)
    output = generate_response(final_prompt)
    print(output)

    matches = re.findall(r"\{[^{}]*\}", output)
    if matches:
        content = matches[0]
        output_dict = eval(content)
        for key in parsed_dict.keys():
            if parsed_dict[key] == "":
                output_dict[key] = ""
    else:
        output_dict = {}
        print("NO OUTPUT")
        pass  # some error handling here maybe

    return output_dict


def get_chart_values(user_input, chart_type):
    ## line or scatter plot
    if "line" in chart_type or "scatter" in chart_type:
        chart_axes_output = line_scatter_chain.predict_and_parse(
            text=f"user_input:{user_input}"
        )["data"]["chart"]
        print(chart_axes_output)
        # reformat the dictionary for matching
        value_dict = {}
        if chart_axes_output:
            value_dict["value1"] = chart_axes_output[0]["yaxis"]
            value_dict["value2"] = chart_axes_output[0]["xaxis"]
            value_dict["path"] = chart_axes_output[0]["path"]
            print(value_dict)
            chart_match_axes = output_match(value_dict, "line_scatter_prompt")
            if chart_match_axes:
                yaxis = chart_match_axes["value1"]
                xaxis = chart_match_axes["value2"]
                path = chart_match_axes["path"]
                return {"yaxis": yaxis, "xaxis": xaxis, "path": path}
        else:
            return "sorry please input some values to plot"

    ## tree plot
    elif "tree" in chart_type:
        filter, new_user_input = tree_check_filter(user_input)
        print(f"filter is {filter}")
        chart_axes_output = treemap_chain.predict_and_parse(
            text=f"user_input:{new_user_input}"
        )["data"]["chart"]
        print(chart_axes_output)
        if len(chart_axes_output) != 0:
            # check paths
            if (
                chart_axes_output[0]["path1"] == ""
                and chart_axes_output[0]["path2"] != ""
            ):
                chart_axes_output[0]["path1"] = chart_axes_output[0]["path2"]
            elif (
                chart_axes_output[0]["path1"] == ""
                and chart_axes_output[0]["path3"] != ""
            ):
                chart_axes_output[0]["path1"] = chart_axes_output[0]["path3"]
            elif (
                chart_axes_output[0]["path2"] == ""
                and chart_axes_output[0]["path3"] != ""
            ):
                chart_axes_output[0]["path2"] = chart_axes_output[0]["path3"]
            if chart_axes_output[0]["path1"] == chart_axes_output[0]["path2"]:
                chart_axes_output[0]["path2"] = ""
            elif chart_axes_output[0]["path2"] == chart_axes_output[0]["path3"]:
                chart_axes_output[0]["path3"] = ""
            # match
            chart_match_axes = output_match(chart_axes_output[0], "tree_prompt")
            if chart_match_axes:
                value = chart_match_axes["value"]
                path1 = chart_match_axes["path1"]
                path2 = chart_match_axes["path2"]
                path3 = chart_match_axes["path3"]
                colour = chart_match_axes["colour_value"]

                if type(filter) == str:
                    filter = [filter]

                ## insert filter logic
                for item in filter:
                    for key in filter_dict.keys():
                        if item.lower() in filter_dict[key]:
                            if path1 == "":
                                path1 = key
                            elif (path2 == "") and (path1 != key):
                                path2 = key
                            elif (path3 == "") and (path2 != key) and (path2 != ""):
                                path3 = key
                
                print(f'VALUE IS {value}')

                return {
                    "value": value,
                    "path1": path1,
                    "path2": path2,
                    "path3": path3,
                    "colour": colour,
                    "filter": filter,
                }
        elif len(chart_axes_output) == 0:
            return "sorry please input some values to plot"

    ## bar plot
    elif "bar" in chart_type:
        chart_axes_output = barchart_chain.predict_and_parse(
            text=f"user_input:{user_input}"
        )["data"]["chart"]
        print(chart_axes_output)
        # reformat the dictionary for matching
        if chart_axes_output:
            chart_match_axes = output_match(chart_axes_output[0], "line_scatter_prompt")
            if chart_match_axes:
                value1 = chart_match_axes["value1"]
                value2 = chart_match_axes["value2"]
                value3 = chart_match_axes["value3"]
                path = chart_match_axes["path"]
                return {
                    "value1": value1,
                    "value2": value2,
                    "value3": value3,
                    "path": path,
                }

        else:
            print("sorry please input some values to plot")

    ## else we default to tree type?
    else:
        chart_axes_output = treemap_chain.predict_and_parse(
            text=f"user_input:{user_input}"
        )["data"]["chart"]
        print(chart_axes_output)
        if len(chart_axes_output) != 0:
            # check paths
            if (
                chart_axes_output[0]["path1"] == ""
                and chart_axes_output[0]["path2"] != ""
            ):
                chart_axes_output[0]["path1"] = chart_axes_output[0]["path2"]
            elif (
                chart_axes_output[0]["path1"] == ""
                and chart_axes_output[0]["path3"] != ""
            ):
                chart_axes_output[0]["path1"] = chart_axes_output[0]["path3"]
            elif (
                chart_axes_output[0]["path2"] == ""
                and chart_axes_output[0]["path3"] != ""
            ):
                chart_axes_output[0]["path2"] = chart_axes_output[0]["path3"]
            if chart_axes_output[0]["path1"] == chart_axes_output[0]["path2"]:
                chart_axes_output[0]["path2"] = ""
            elif chart_axes_output[0]["path2"] == chart_axes_output[0]["path3"]:
                chart_axes_output[0]["path3"] = ""
            # match
            chart_match_axes = output_match(chart_axes_output[0], "tree_prompt")
            if chart_match_axes:
                value = chart_match_axes["value"]
                path1 = chart_match_axes["path1"]
                path2 = chart_match_axes["path2"]
                path3 = chart_match_axes["path3"]
                return {"value": value, "path1": path1, "path2": path2, "path3": path3}
        elif len(chart_axes_output) == 0:
            return "sorry please input some values to plot"


def tree_check_filter(user_input):
    filter_dict = {}
    filter_prompt = f""" 
    Based on the input string below, extract the closest matches from the list below. If there is no match, return an empty string.
    There may also be multiple matches. In string_without_matches output the exact user input while removing the matched string, try to complete the sentence 
    - list = ["USA","UK","France","Germany","Italy","Spain","Japan","South Korea","China","Thailand","Australia","Canada","Russia","India","Egypt",
    "North America","Europe","Asia", "Africa", "New York", "Los Angeles","Chicago","Houston","Miami","London","Paris","Berlin","Rome","Madrid","Tokyo",
    "Seoul","Beijing","Shanghai","Bangkok","Sydney","Melbourne","Toronto","Vancouver","Moscow","Mumbai","Cairo"]


    Format the output in json with the following keys, just return the json output do not include additional words:
    - match - output a list of the closest match based on the list above, do not include extra matches. Only output exact items from the list, do not output your own values.
    - string_without_match - output the user input as a complete sentence and remove the matched keywords. Output a complete grammatical sentence, remove additional words like 'and','of','in' if necessary. DO NOT add any words or paraphrase the user input. 

    Example 1:
    User Input = plot a treeplot of bookings in france and UK
    match: ["France", "UK"]
    string_without_match: "plot a treeplot of bookings"

    Example 2:
    user Input = plot a treeplot of acv bookings in region l2 with a color of acv yoy%
    match: []
    string_without_match: "plot a treeplot of acv bookings in region l2 with a color of acv yoy%"


    Example 3:
    User input = treeplot of revenue in china 
    match: ['china']
    string_without_match: "treeplot of revenue"

    
    Input below:
    {user_input}
    """
    output = generate_response(filter_prompt)
    matches = re.findall(r"\{[^{}]*\}", output)
    if matches:
        content = matches[0]
        filter_dict = eval(content)
        try:
            filter = filter_dict["match"]
            new_user_input = filter_dict["string_without_match"]
        except:
            filter = ""
            new_user_input = user_input

    print(f"filter found: {filter}")
    print(f"new user input: {new_user_input}")

    return filter, new_user_input


#### For testing purposes
###############################
# user_input = "plot a line plot by each Industry Sector by each material ID of win rate and ACV bookings"
# user_input = 'line plot of acv bookings and revenue in region l1'
user_input = "plot a scatter plot by each Industry Sector of win rate and ACV bookings"
user_input = "line plot of acv bookings and revenue % in region l1"
user_input = "line plot of acv bookings and revenue in region l1"
user_input = "tree map by region l2 and region l3 of the acv bookings"
user_input = "scatter plot of number of AEs and %private bookings by CAAs"
user_input = "tree map of booking in region l2 by country"
user_input = "scatter plot of bookings in region l2 and region l3"
user_input = "treemap of revenue in region l2 and region l3 and by country"
user_input = "treemap of revenue and win rate"
user_input = "scatter plot of number of aes and revenue growth by country"
user_input = "scatter plot of private bookings by caas and acv bookings"
user_input = "scatter plot of market share in percent and market year on year"
user_input = "plot a tree map of region l1, win rate"
user_input = "treemap, regionl1, winrate"
user_input = "plot a treeplot in regionl2 of winrate"
user_input = "plot a treeplot in region l3 of avgdealsize"
# user_input = "treeplot, region l1, copa revenue"
# user_input = 'scatter plot of market share in percent and market year on year'

user_input = "treemap of revenue in region l2 and region l3 and by country"
user_input = "tree map by region l2 and region l3 of the acv bookings"

user_input = "plot a scatter plot by each Industry Sector of win rate and ACV bookings"
user_input = "treeplot, region l2, bookings"
# user_input = 'treeplot, bookings, region l2'
user_input = "treeplot, revenue, region l3"
user_input = "treeplot, revenue, country"
user_input = "treemap of win rate and bookings"
user_input = "treemap of revenue and bookings"
user_input = "plot a treeplot in region l2 of avgdealsize"
# user_input = 'plot a treemap of copa revenue in different countries'
user_input = "plot a barchart of copa revenue and win rate in different countries"
user_input = "plot a treeplot of copa revenue in region l2 of CS france and CS belux with a color of acv bookings"
user_input = (
    "plot a treeplot of copa revenue in region l2 of and with a color of acv bookings"
)
user_input = "plot a treemap of bookings of  and  in region l3 with colour win rate"
user_input = "plot a treemap of acv yoy% in Sl-bel mm, and cs france mm head in region l3, color to be avg deal size"
user_input = "plot a treeplot of copa revenue of region country of france and netherlands with a color of acv bookings"
user_input = "plot a treeplot of copa revenue of france and CS netherlands and Sl-bel mm with a color of acv bookings"
user_input = "plot a treeplot of win rate in netherlands, france and UK with a color of acv bookings"
user_input = "plot a treeplot of acv bookings in netherlands, norway, UK and france with colour of revenue"
user_input = "plot a treeplot of acv bookings in netherlands, norway, UK and france with colour of revenue"
user_input = "treeplot of CS UKI and SL UKI mm head and SL UKI consumer of the revenue with colour as the avg deal size"
user_input = "treeplot of CS UKI and SL UKI mm head and SL UKI consumer of the revenue with colour as the avg deal size"
user_input = "plot a treeplot of bookings of france and colour as rev yoy%"
user_input = "plot a treeplot of bookings in cs france and cs nordic and cs uki"
user_input = "treeplot of CS UKI mm head and SL UKI consumer of the revenue with colour as the avg deal size"


chart_type = ""
chart_type_output = chart_type_chain.predict_and_parse(
    text=f"user_input:{user_input}, chart_type_list:{chart_list}"
)["data"]["chart"]
if len(chart_type_output) != 0:
    chart_type = chart_type_output[0]["chart_type"]
    print(chart_type)
else:
    print("sorry, we cannot find a chart type to plot")


## line or scatter plot
if "line" in chart_type or "scatter" in chart_type:
    chart_axes_output = line_scatter_chain.predict_and_parse(
        text=f"user_input:{user_input}"
    )["data"]["chart"]
    print(chart_axes_output)

    # reformat the dictionary for matching
    value_dict = {}
    if chart_axes_output:
        value_dict["value1"] = chart_axes_output[0]["yaxis"]
        value_dict["value2"] = chart_axes_output[0]["xaxis"]
        value_dict["path"] = chart_axes_output[0]["path"]
        print(value_dict)
        chart_match_axes = output_match(value_dict, "line_scatter_prompt")
        if chart_match_axes:
            yaxis = chart_match_axes["value1"]
            xaxis = chart_match_axes["value2"]
            path = chart_match_axes["path"]
            print(yaxis)
            print(xaxis)
            print(path)
    else:
        print("sorry please input some values to plot")

## tree plot
elif "tree" in chart_type:
    filter, new_user_input = tree_check_filter(user_input)
    chart_axes_output = treemap_chain.predict_and_parse(
        text=f"user_input:{new_user_input}"
    )["data"]["chart"]
    print(chart_axes_output)
    if len(chart_axes_output) != 0:
        # check paths
        if chart_axes_output[0]["path1"] == "" and chart_axes_output[0]["path2"] != "":
            chart_axes_output[0]["path1"] = chart_axes_output[0]["path2"]
        elif (
            chart_axes_output[0]["path1"] == "" and chart_axes_output[0]["path3"] != ""
        ):
            chart_axes_output[0]["path1"] = chart_axes_output[0]["path3"]
        elif (
            chart_axes_output[0]["path2"] == "" and chart_axes_output[0]["path3"] != ""
        ):
            chart_axes_output[0]["path2"] = chart_axes_output[0]["path3"]
        if chart_axes_output[0]["path1"] == chart_axes_output[0]["path2"]:
            chart_axes_output[0]["path2"] = ""
        elif chart_axes_output[0]["path2"] == chart_axes_output[0]["path3"]:
            chart_axes_output[0]["path3"] = ""
        # match
        chart_match_axes = output_match(chart_axes_output[0], "tree_prompt")
        print(chart_match_axes)
        if chart_match_axes:
            value = chart_match_axes["value"]
            path1 = chart_match_axes["path1"]
            path2 = chart_match_axes["path2"]
            path3 = chart_match_axes["path3"]
            colour = chart_match_axes["colour_value"]
            chart_match_axes["filter"] = filter

            # check filter and path
            for item in filter:
                for key in filter_dict.keys():
                    if item in filter_dict[key]:
                        if path1 == "":
                            path1 = key
                        elif (path2 == "") and (path1 != key):
                            path2 = key
                        elif (path3 == "") and (path2 != key) and (path2 != ""):
                            path3 = key

            print(f"value: {value}")
            print(f"path1: {path1}")
            print(f"path2: {path2}")
            print(f"path3: {path3}")
            print(f"colour: {colour}")
            print(f"filter: {filter}")
    elif len(chart_axes_output) == 0:
        print("sorry please input some values to plot")

## bar plot
elif "bar" in chart_type:
    chart_axes_output = barchart_chain.predict_and_parse(
        text=f"user_input:{user_input}"
    )["data"]["chart"]
    print(chart_axes_output)
    # reformat the dictionary for matching
    if chart_axes_output:
        chart_match_axes = output_match(chart_axes_output[0], "line_scatter_prompt")
        if chart_match_axes:
            value1 = chart_match_axes["value1"]
            value2 = chart_match_axes["value2"]
            path = chart_match_axes["path"]
            print(value1)
            print(value2)
            print(path)
    else:
        print("sorry please input some values to plot")


# In[ ]:
