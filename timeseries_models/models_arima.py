from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import Holt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.api import SimpleExpSmoothing, ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.interpolate import interp1d
import pmdarima as pm

import matplotlib.pyplot as plt 
from pandas import Series
import pandas as pd 
import numpy as np
import seaborn as sns


def train_ARIMA(train_df, test_df, target_column):
  model = ARIMA(train_df[target_column].values, order=(2,1,1))
  model = model.fit()
  start = len(train_df)
  end  = len(train_df) + len(test_df) -1
  test_pred = model.predict(start=start, end=end, dynamic=False, typ="levels")
  test_df['pred'] = test_pred
  return test_df

def cal_growth(df,year, target_column, date):
  dic_growth = {}
  dic_growth['Q1'] =  round((((df[(df[date].dt.year == year) & (df[date].dt.month <= 3)][target_column].sum())/ (df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 3)][target_column].sum()))-1) *100, 1)
  dic_growth['Q2'] =  round((((df[(df[date].dt.year == year) & (df[date].dt.month <= 6)][target_column].sum())/ (df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 6)][target_column].sum()))-1) *100, 1)
  dic_growth['Q3'] =  round((((df[(df[date].dt.year == year) & (df[date].dt.month <= 9)][target_column].sum())/ (df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 9)][target_column].sum()))-1) *100, 1)
  dic_growth['Q4'] =  round((((df[(df[date].dt.year == year) & (df[date].dt.month <= 12)][target_column].sum())/ (df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 12)][target_column].sum()))-1) *100, 1)
  return dic_growth

def cal_forecast_arima(df,year, target_column, date):
  dic_forecast={}
  prev_year = df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 12)][target_column].sum()

   #Q1 train 
  train_df = df[df['Date'] < str(year)+'-01-01']
  test_df =  df[(df[date].dt.year == year) & (df[date].dt.month > 0)]
  test_pred = train_ARIMA(train_df, test_df, 'Total Merchandise Trade')
   
   #Q1 calculate
  pred_val = test_pred['pred'].sum()
  yoy_growth = (((pred_val)/prev_year) -1)*100
  dic_forecast['Q1'] = round(yoy_growth,1)

   #Q1 plot
  plot_q1 = test_pred[(test_pred[date].dt.year <= (year)) & (test_pred[date].dt.month <= 3)]

   #Q2 train 
  train_df = df[df['Date'] < str(year)+'-04-01']
  test_df =  df[(df[date].dt.year == year) & (df[date].dt.month > 3)]
  test_pred = train_ARIMA(train_df, test_df, 'Total Merchandise Trade')

   #Q2 calculate
  actual_val = df[(df[date].dt.year == (year)) & (df[date].dt.month <= 3)][target_column].sum()
  pred_val = test_pred['pred'].sum()
  yoy_growth = (((actual_val+pred_val)/prev_year) -1)*100
  dic_forecast['Q2'] = round(yoy_growth,1)

   #Q2 plot
  plot_q2 = test_pred[(test_pred[date].dt.year <= (year)) & (test_pred[date].dt.month > 3) & (test_pred[date].dt.month <= 6)]
   
   #Q3 train 
  train_df = df[df['Date'] < str(year)+'-06-01']
  test_df =  df[(df[date].dt.year == year) & (df[date].dt.month > 6)]
  test_pred = train_ARIMA(train_df, test_df, 'Total Merchandise Trade')

   #Q3 calculate
  actual_val = df[(df[date].dt.year == (year)) & (df[date].dt.month <= 6)][target_column].sum()
  pred_val = test_pred['pred'].sum()
  yoy_growth = (((actual_val+pred_val)/prev_year) -1)*100
  dic_forecast['Q3'] = round(yoy_growth,1)

   #Q3 plot
  plot_q3 = test_pred[(test_pred[date].dt.year <= (year)) & (test_pred[date].dt.month > 6) & (test_pred[date].dt.month <= 9)]
   
   #Q4 train 
  train_df = df[df['Date'] < str(year)+'-09-01']
  test_df =  df[(df[date].dt.year == year) & (df[date].dt.month > 9)]
  test_pred = train_ARIMA(train_df, test_df, 'Total Merchandise Trade')

   #Q4 calculate
  actual_val = df[(df[date].dt.year == (year)) & (df[date].dt.month <= 9)][target_column].sum()
  pred_val = test_pred['pred'].sum()
  yoy_growth = (((actual_val+pred_val)/prev_year) -1)*100
  dic_forecast['Q4'] = round(yoy_growth,1)
   
   #Q4 plot
  plot_q4 = test_pred[(test_pred[date].dt.year <= (year)) & (test_pred[date].dt.month > 9) & (test_pred[date].dt.month <= 12)]

  plot = pd.concat([plot_q1, plot_q2, plot_q3, plot_q4])
   
  return dic_forecast, plot


def plot_image(actual_df, pred_df, max_year, target_column, date_column, filepath):
  sns.set_theme()
  plt.figure(figsize=(15, 8))
  actual = actual_df[(actual_df[date_column].dt.year >= max_year)]
  sns.lineplot(x = date_column, y = target_column, data = actual, color = 'green', label='Actual')
  #sns.lineplot(x = date_column, y = 'pred', data = train_df, color = 'blue', label='Train Predictions')
  sns.lineplot(x = date_column, y = 'pred', data = pred_df, color = 'red', label = 'Test Predictions')
  plt.savefig(filepath)

