import math
import pandas_datareader as web
import numpy as np
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 
import random
#import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.models import load_model
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import json 


import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import tensorflow as tf

def build_train2(df, year, target_column, date, quarter):
  """
  build x_train and y_train datasets, set quarter
  """
  if quarter==1:
    ### Q1 train 
    training_data = df[df['Date'] < str(year)+'-01-01'][target_column].values
  elif quarter==2:
    ### Q2 train 
    training_data = df[df['Date'] < str(year)+'-04-01'][target_column].values
  elif quarter ==3:
    ### Q3 train 
    training_data = df[df['Date'] < str(year)+'-07-01'][target_column].values
  elif quarter==4:
    training_data = df[df['Date'] < str(year)+'-10-01'][target_column].values


  # Scale values
  scaler = MinMaxScaler(feature_range=(0,1))
  train_data = scaler.fit_transform(training_data.reshape(-1, 1) )
  
  #split the data into x_train and y_train
  x_train = []
  y_train = []
  
  for i in range(12, len(train_data)):
    x_train.append(train_data[i-12:i,0])
    y_train.append(train_data[i,0])

  #convert the x_train and y_train to numpy arrays 
  x_train, y_train = np.array(x_train), np.array(y_train)
  x_train = np.reshape(x_train,(x_train.shape[0], x_train.shape[1],1))

  return x_train, y_train 

def build_input(df, year, target_column, date, quarter): 
  ### Q1 test 
  if quarter==1:
    ### Q1 train 
    training_data = df[(df['Date'] >= str(year-1)+'-01-01') & (df['Date'] < str(year)+'-01-01')][target_column].values
  elif quarter==2:
    ### Q2 train 
    training_data = df[(df['Date'] >= str(year-1)+'-04-01') & (df['Date'] < str(year)+'-04-01')][target_column].values
  elif quarter ==3:
    ### Q3 train 
    training_data = df[(df['Date'] >= str(year-1)+'-07-01') & (df['Date'] < str(year)+'-07-01')][target_column].values
  elif quarter==4:
    training_data = df[(df['Date'] >= str(year-1)+'-10-01') & (df['Date'] < str(year)+'-10-01')][target_column].values

  return training_data

def lstm_model3(x_train, y_train):

  random.seed(42)
  np.random.seed(42)

  ### Build Model 
  model = Sequential()
  model.add(LSTM(4, input_shape=(x_train.shape[1], x_train.shape[2]), return_sequences=True))
  model.add(LSTM(3, return_sequences=False))
  model.add(Dense(1))

  ### Compile
  model.compile(optimizer='adam', loss='mean_squared_error')

  #Train the model
  model.fit(x_train, y_train, batch_size=1, epochs=1)

  # Predict
  model.save('lstm_model.h5')
  return model 

def predict_steps_ahead(model_file, test_data, steps_ahead):
  # load model
  model = load_model(model_file)

  predictions = []
  
  for i in range(steps_ahead):
    scaler = MinMaxScaler(feature_range=(0,1))
    last_12_data_scaled = scaler.fit_transform(test_data.reshape(-1, 1) )
    last_12_data_scaled = test_data.reshape(-1, 1)
    X_test = []
    X_test.append(last_12_data_scaled)
    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1],1))
    
    prediction = model.predict(X_test)
    prediction = scaler.inverse_transform(prediction)
    predictions.append(prediction[0][0])
    test_data = np.append(test_data, prediction)
    test_data = test_data[1:]
    
  return predictions

def cal_forecast_lstm(df, year, target_column, date):
  dic_forecast = {}
  prev_year = df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 12)][target_column].sum()

  ## Q1 Train 
  x_train, y_train= build_train2(df, 2022, "Total Merchandise Trade", "Date", 1)
  input_data = build_input(df, 2022, "Total Merchandise Trade", "Date", 1)
  lstm_model3(x_train,y_train)
  q1_pred = predict_steps_ahead('lstm_model.h5', input_data, 3)

  ##Q1 calculate 
  prev_q1 = df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 3)][target_column].sum()
  dic_forecast['Q1'] = round((((sum(q1_pred))/prev_q1) -1)*100,1)

  ## Q2 Train 
  x_train, y_train= build_train2(df, 2022, "Total Merchandise Trade", "Date", 2)
  input_data = build_input(df, 2022, "Total Merchandise Trade", "Date", 2)
  lstm_model3(x_train,y_train)
  q2_pred = predict_steps_ahead('lstm_model.h5', input_data, 3)

  ##Q2 calculate 
  prev_q2 = df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 6)][target_column].sum()
  now_q1 = df[(df[date].dt.year == (year)) & (df[date].dt.month <= 3)][target_column].sum()
  cum_pred = now_q1 + sum(q2_pred)
  dic_forecast['Q2'] = round((((cum_pred)/prev_q2) -1)*100,1)

  ## Q3 Train 
  x_train, y_train= build_train2(df, 2022, "Total Merchandise Trade", "Date", 3)
  input_data = build_input(df, 2022, "Total Merchandise Trade", "Date", 3)
  lstm_model3(x_train,y_train)
  q3_pred = predict_steps_ahead('lstm_model.h5', input_data, 3)

  ##Q3 calculate 
  prev_q3 = df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 9)][target_column].sum()
  now_q2 = df[(df[date].dt.year == (year)) & (df[date].dt.month <= 6)][target_column].sum()
  cum_pred = now_q2 + sum(q3_pred)
  dic_forecast['Q3'] = round((((cum_pred)/prev_q3) -1)*100,1)

  ## Q4 Train 
  x_train, y_train= build_train2(df, 2022, "Total Merchandise Trade", "Date", 4)
  input_data = build_input(df, 2022, "Total Merchandise Trade", "Date", 4)
  lstm_model3(x_train,y_train)
  q4_pred = predict_steps_ahead('lstm_model.h5', input_data, 3)

  ##Q4 calculate 
  prev_q4 = df[(df[date].dt.year == (year-1)) & (df[date].dt.month <= 12)][target_column].sum()
  now_q3 = df[(df[date].dt.year == (year)) & (df[date].dt.month <= 9)][target_column].sum()
  cum_pred = now_q3 + sum(q4_pred)
  dic_forecast['Q4'] = round((((cum_pred)/prev_q4) -1)*100,1)

  ##plot 
  start_date = str(year)+'-01-01'
  end_date = str(year)+'-12-31'
  date_range = pd.date_range(start=start_date, end=end_date, freq='M')
  list_pred = q1_pred + q2_pred + q3_pred + q4_pred 
  pred_df = pd.DataFrame(date_range, columns=['Date'])
  pred_df['pred'] = list_pred

  return dic_forecast, pred_df

### draw a plot
def plot_image(actual_df, pred_df, max_year, target_column, date_column, filepath):
  sns.set_theme()
  plt.figure(figsize=(15, 8))
  actual = actual_df[(actual_df[date_column].dt.year >= max_year)]
  sns.lineplot(x = date_column, y = target_column, data = actual, color = 'green', label='Actual')
  #sns.lineplot(x = date_column, y = 'pred', data = train_df, color = 'blue', label='Train Predictions')
  sns.lineplot(x = date_column, y = 'pred', data = pred_df, color = 'red', label = 'Test Predictions')
  plt.savefig(filepath)


# df = pd.read_excel("Trade data.xlsx")
# dic_forecast, pred_df = cal_forecast_lstm(df,2022, "Total Merchandise Trade", "Date")

# ###Open a file for writing
# with open('dict.json', 'w') as f:
#     json.dump(dic_forecast, f)

# print(dic_forecast)


# plot_image(df, pred_df, 2010, 'Total Merchandise Trade', 'Date', 'static/lstm.png')

