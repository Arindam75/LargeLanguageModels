from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai 

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

##Function to load Gemini Pro model and get repsonses

model = genai.GenerativeModel("gemini-pro")
def get_gemini_response(question):

    response = model.generate_content(question)
    return response.text

## Initialize the Streamlit App

st.set_page_config(page_title = "Q&A Demo")

st.header("Gemini LLM Application")

input = st.text_input("Input: ", key = "input")
submit = st.button("Submit")

## When Submit is Clicked

if submit:

    response = get_gemini_response(input)
    st.subheader("The Response Is : ")
    st.write(response)