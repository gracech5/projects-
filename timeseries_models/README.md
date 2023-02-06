## Time Series Model Web Application (work in progress)

The purpose of the time series model web application is to showcase the performance of machine learning models in forecasting Singapore's total merchandise trade.
Total merchandise trade data was downloaded from the Department of Statistics [Singstat portal](https://www.singstat.gov.sg/) 

<img width="824" alt="image" src="https://user-images.githubusercontent.com/119866759/217029009-d80e1cf1-17e3-4296-9750-46b61992db29.png">

I developed a simple web application as part of a personal project to build on my Flask and web development skills. I hope the user would be able to have a quick visual, overview of the performance of the different time series machine learning models without having to write code. A visual plot is drawn and the year-on-year growth rates over the different quarters are reported, since trade data is forecasted every quarter in Singapore. 

<img width="893" alt="image" src="https://user-images.githubusercontent.com/119866759/217030388-f5844f33-6c54-4a61-a31b-665efd806f3c.png">

An ARIMA model of (2,1,1) was chosen based on the auto-ARIMA library. More work is needed to further finetune the LSTM neural netowrk model. 
This application is a work in progress, I hope to add a year filter to show the performance of these models in different years. 

Note: the ARIMA model is retrained when the application is running, but the LSTM model and the results have been loaded in as it takes a while for the model to run 


To run the web application, download the folder and run the following lines in the terminal:
- pip install -r requirements.txt
- python app.py 



