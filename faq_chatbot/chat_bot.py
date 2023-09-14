import streamlit as st
import requests
import json
from functions import get_data, get_list_products, get_products, generate_pdt_info,  generate_response, generate_reply

#################### context ###################################
context = [
    {"role": "assistant", "content": "You are a friendly help chatbot to answer user's queries about products. Do not add your own information. Be concise in your reply. "}
]

################### for chat ##################################
# add memory
if 'product_global' not in st.session_state:
    st.session_state['product_global'] = []

if 'context' not in st.session_state:
    st.session_state['context'] = context 

if 'data' not in st.session_state:
    st.session_state['data'] = get_data()


# ################# Chat Bot #######################################################

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there, ask me about a product."}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            final_pdt_list = get_products(st.session_state['data'], user_input)
            pdt_info = generate_pdt_info(final_pdt_list, st.session_state['data'])
            response =  generate_reply(user_input, pdt_info, st.session_state['context'])
            print(f"CONTEXT IS {st.session_state['context']}")
            st.markdown(response)

            #add memory?
            st.session_state['context'].append({"role": "assistant", "content": response})
            
            if len(st.session_state['context'])>7:
                st.session_state['context'].pop(1)
                st.session_state['context'].pop(1)

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
