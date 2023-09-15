## FAQ Chatbot

### Introduction

This is a simple chatbot built using GPT that is customised to answer questions from a simple FAQ about products.
Sample data was generated and summarised using GPT in the data folder. 

Some examples of the capabilities of the chatbot are shown below, the chatbot can be used to answer generic questions about products in general

<img width="412" alt="image" src="https://github.com/gracech5/projects-/assets/119866759/3eb153fa-bda2-462f-b10b-13d511283517">

and can also be used to answer questions about a specific product: 

<img width="412" alt="image" src="https://github.com/gracech5/projects-/assets/119866759/53ef94ce-50fe-4665-b554-cd15b89fcde8">



### Instructions 

To run this application, you need to have an Open AI API Key. Create a `.env` file in the `/backend` folder and set the following parameters in the .env file:

```bash
OPENAI_API_KEY = 'YOUR-API-KEY-HERE'

DATA_FILEPATH = 'data/fake_products_summary.csv'

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

Finally, run the application on Streamlit using the following command:
```bash
streamlit run chat_bot.py
```
