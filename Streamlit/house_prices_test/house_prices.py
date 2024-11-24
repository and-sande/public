import streamlit as st
import pandas as pd
from pycaret.regression import load_model, predict_model
import os

# Debugging: Print the current working directory and list files
print("Current working directory:", os.getcwd())
print("Files in the current directory:", os.listdir("."))

# Load the trained model
model = load_model("./best_regression_model")  # Replace with your saved model name

# Title for the app
st.title("House Price Prediction App")

# User inputs for the features
size = st.slider("Size (in sq. ft.):", min_value=500, max_value=3500, step=50)
bedrooms = st.selectbox("Number of Bedrooms:", options=[1, 2, 3, 4, 5])
age = st.slider("Age of the House (in years):", min_value=0, max_value=30, step=1)

# Create input data for the model
input_data = pd.DataFrame({
    "Size": [size],
    "Bedrooms": [bedrooms],
    "Age": [age]
})

# Predict the price
if st.button("Predict Price"):
    prediction = predict_model(model, data=input_data)
    st.success(f"The estimated price is: ${prediction['prediction_label'][0]:,.2f}")
