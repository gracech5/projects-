import os
import requests
import json 
from dotenv import load_dotenv
import os 
import pandas as pd 
import ast



load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DATA_FILEPATH = os.environ.get("DATA_FILEPATH")


######### GPT generate response function ##########################

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
        "temperature": 0
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
    

def chat_response(context):
    # Define the API endpoint URL
        url = "https://api.openai.com/v1/chat/completions"

        # Define the message data
        data = {
            "model": "gpt-3.5-turbo",
            "messages": context
        }

        # Define the headers including your API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        # Make the POST request to the API
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # Get the JSON response
        response_data = response.json()

            # Process the response
        if response.status_code == 200:
            response_data = response.json()
            completed_message = response_data['choices'][0]['message']['content']
            return(completed_message)
        else:
            return(f"API request failed with status code {response.status_code}: {response.text}")


######### Get data function ##################

def get_data():
    df = pd.read_csv(DATA_FILEPATH)
    return df

######## Get products function ###############

def get_list_products(df):
    pdt_list = []
    for i in range(len(df)):
        pdt_description = f"Product Name: {df['Product Name'].iloc[i]} \nInfo: {df['Summarised Description'].iloc[i]}"
        print(pdt_description)
        pdt_list.append(pdt_description)
    return pdt_list

def get_products(df, user_query):
    pdt_list = get_list_products(df)
    product_prompt = f"""

    You are a helpful assistant trying to help the user find the best product for their use case. Based on the full list of 
    products and their descriptions below. Extract the relevant products and output the full product name in a list. 
    Do not generate your own products. There may be multiple products related to the user query.

    Example: 
    user_query: I would like to find out more about a cloud service
    Ans: ['CloudSync X']

    ******************
    User_query: {user_query}
    Product_list: {pdt_list}

    """
    output = generate_response(product_prompt)
    final_pdt_list = ast.literal_eval(output)

    return final_pdt_list


def generate_pdt_info(final_pdt_list, df):
    """
    Generate background info on each product based on the final list of products
    """
    filtered_df = df[df['Product Name'].isin(final_pdt_list)]
    pdt_info = []
    for i in range(len(filtered_df)):
        pdt_description = f"Product Name: {filtered_df['Product Name'].iloc[i]} \nInfo: {filtered_df['Full Description'].iloc[i]}"
        print(pdt_description)
        pdt_info.append(pdt_description)
        
    return pdt_info 

def generate_reply(user_query, pdt_info, existing_context):
    """
    takes in the existing chat context and adds in the new user query
    before sending it to GPT to get a response
    """
    existing_context.append({'role': 'user', 'content':user_query})
    existing_context.append({'role':'system', 'content':f""" Answer the user's latest query above based on the following background info in a concise manner:
    background info: {pdt_info}
    """})
    response = chat_response(existing_context)
    return response


