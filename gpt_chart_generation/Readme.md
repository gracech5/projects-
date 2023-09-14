# GPT Chart Generation Application 

## Introduction

This application seeks to simplify the business intelligence process by enabling the user to automatically search for a chart of interest.
Instead of having to manually click and specify their requirements, this project explores the possibility of enabling users to simplify specify in a 
search bar their chart of interest e.g. 'bar plot of COPA revenue in Europe' for example.

To explore this possibility, a fake_data.csv dataset was created in the data folder, containing randomly generated data on COPA (Revenue), avg deal size, rev yoy% etc
across different regions. Region L1 displays the data at continent level, region L2 at country level and Region L3 at the city level. 

This application uses GPT 3.5, you can modify the model used in the backend in the  `backend_schema.py` file. 

## Deployment Steps

To deploy this application, you need to have an Open AI API Key. Create a `.env` file in the `/backend` folder and set the following parameters in the .env file:
```bash
OPENAI_API_KEY = 'YOUR-API-KEY-HERE'

DATA_FILEPATH = 'data/fake_data.csv'

```
Next, set up a virtual environment and install the requirements 
```bash
#create a virtual env
python -m venv venv

#activate the virtual env
venv\Scripts\activate

#install requirements
pip install -r requirements.txt
```

Finally, run the backend on fastAPI using the following command:
```bash
python main2.py 
```

To set up the frontend, go to the frontend folder and run the following commands to install the node modules
```bash
npm install
```

To run the frontend, use the following command:
```bash
npm run serve
```

