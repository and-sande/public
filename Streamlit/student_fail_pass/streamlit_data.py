import streamlit as st
import pickle
import joblib

# Load your trained model
import os

# Get the absolute path to the .pkl file
model_path = os.path.abspath('student_performance_model.pkl')
model = joblib.load(model_path)

# Title of the app
st.title("Student Performance Predictor")

# Input fields for student data
st.header("Enter Student Data")
attendance = st.slider("Attendance (%)", 0, 100, 50)
assignment_scores = st.slider("Assignment Scores", 0, 100, 50)
midterm_scores = st.slider("Midterm Scores", 0, 100, 50)

# Predict button
if st.button("Predict"):
    # Prepare input data for the model
    input_data = [[attendance, assignment_scores, midterm_scores]]
    
    # Make a prediction
    prediction = model.predict(input_data)
    
    # Display the result
    if prediction[0] == 1:
        st.success("This student is predicted to **PASS**.")
    else:
        st.error("This student is predicted to **FAIL**.")