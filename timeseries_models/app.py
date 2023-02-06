from flask import Flask, render_template, request, url_for, redirect
from forms import arima, lstm
#from flask_sqlalchemy import SQLAlchemy 
from models_arima import cal_growth, cal_forecast_arima, plot_image
#from models_lstm import build_train2, build_input, lstm_model3, predict_steps_ahead, cal_forecast_lstm
import numpy as np 
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
#import plotly.express as px 
#import plotly.graph_objects as go
#from kaleido.scopes.plotly import PlotlyScope

import matplotlib.pyplot as plt 
from pandas import Series
import pandas as pd 
import numpy as np
import seaborn as sns
import json 

# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = ""

# import tensorflow as tf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route("/", methods=['GET','POST'])
def index():
    form = arima()
    return render_template('index.html')


@app.route("/lstm", methods=['GET','POST'])
def lstm():
    df = pd.read_excel("Trade data.xlsx")

    ### actual growth rates 
    dic_growth = cal_growth(df, 2022, 'Total Merchandise Trade', 'Date')
    q1 = dic_growth['Q1']
    q2 = dic_growth['Q2']
    q3 = dic_growth['Q3']
    q4 = dic_growth['Q4']

    ### forecasted growth rates  
    with open('dict.json', 'r') as f:
        data = json.load(f)
    dic_forecast = data  
    f1 = dic_forecast['Q1']
    f2 = dic_forecast['Q2']
    f3 = dic_forecast['Q3']
    f4 = dic_forecast['Q4']

    return render_template('lstm.html', q1=q1, q2=q2, q3=q3, q4=q4, f1=f1, f2=f2, f3=f3, f4=f4)



@app.route("/arima", methods=['GET','POST'])
def arima():
    df = pd.read_excel("Trade data.xlsx")

    ### actual growth rates 
    dic_growth = cal_growth(df, 2022, 'Total Merchandise Trade', 'Date')
    q1 = dic_growth['Q1']
    q2 = dic_growth['Q2']
    q3 = dic_growth['Q3']
    q4 = dic_growth['Q4']

    ### forecasted growth rates  
    dic_forecast, plot = cal_forecast_arima(df, 2022, 'Total Merchandise Trade', 'Date')  
    f1 = dic_forecast['Q1']
    f2 = dic_forecast['Q2']
    f3 = dic_forecast['Q3']
    f4 = dic_forecast['Q4']

    ### plot image
    plot_image(df,plot,2010, 'Total Merchandise Trade', 'Date','static/arima.png')

    ## return page
    return render_template('arima.html', q1=q1, q2=q2, q3=q3, q4=q4, f1=f1, f2=f2, f3=f3, f4=f4)



if __name__ == '__main__':
    app.run(debug=True)