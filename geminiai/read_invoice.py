from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

##Function to load Gemini Pro model and get repsonses

model = genai.GenerativeModel("gemini-pro-vision")


def get_gemini_response(input, image, prompt):

    response = model.generate_content([input, image[0], prompt])
    print(response)
    return response.text

def input_image_setup(uploaded_file):

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type":uploaded_file.type,
                "data":bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No image found")

st.set_page_config(page_title = "Multilanguage Invoice Extractor")

st.header("Gemini LLM Application")
input = st.text_input("Input Prompt: ", key = "input")
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

image =""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

submit = st.button("Tell me about the image")

input_prompt = """
You are an expert in understanding invoices. We will upload an image as invoice
and you will have to answer any question based on the uploaded invoice image
"""

if submit:

    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)

    st.subheader("The Response Is : ")
    st.write(response)



