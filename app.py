# app.py

import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# -----------------------
# Load Environment Variables
# -----------------------
load_dotenv()
API_KEY = os.getenv("IBM_API_KEY")
DEPLOYMENT_URL = os.getenv("IBM_DEPLOYMENT_URL")

# -----------------------
# Get Access Token
# -----------------------
def get_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"apikey={api_key}&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    res = requests.post(url, headers=headers, data=data)
    return res.json()["access_token"]

# -----------------------
# Get Salary Prediction
# -----------------------
def get_prediction(values):
    token = get_token(API_KEY)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "input_data": [
            {
                "fields": [
                    "ID", "education_level", "years_experience", "job_title",
                    "industry", "location", "company_size", "certifications",
                    "age", "working_hours", "crucial_code"
                ],
                "values": [values]
            }
        ]
    }

    response = requests.post(DEPLOYMENT_URL, headers=headers, json=payload)
    return response.json()

# -----------------------
# Streamlit UI
# -----------------------
st.markdown("<h1 style='text-align: center; color: #00FFFF;'>Salary Predictor</h1>", unsafe_allow_html=True)
st.markdown("---")

# Input Section
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        id_val = st.text_input("👤 User ID", placeholder="Enter user ID")
        education = st.selectbox("🎓 Education Level", ["High School", "Bachelor", "Master", "PhD"])
        experience = st.number_input("📊 Years of Experience", min_value=0.0, step=0.5)
        job = st.text_input("💼 Job Title", placeholder="e.g. Data Scientist")
        industry = st.text_input("🏭 Industry", placeholder="e.g. Education")

    with col2:
        location = st.text_input("📍 Location", placeholder="e.g. New York")
        company_size = st.selectbox("🏢 Company Size", ["Small", "Medium", "Large"])
        certs = st.number_input("📜 Number of Certifications", min_value=0)
        age = st.number_input("🔢 Age", min_value=18, max_value=100)
        hours = st.number_input("⏰ Working Hours/Week", min_value=1, max_value=168)
        code = st.text_input("🔑 Crucial Code (if any)")

    submitted = st.form_submit_button("🔮 Predict Salary")

# -----------------------
# Prediction Result
# -----------------------
if submitted:
    user_input = [
        id_val, education, experience, job, industry,
        location, company_size, certs, age, hours, code
    ]
    with st.spinner("Fetching prediction from AutoAI model..."):
        try:
            result = get_prediction(user_input)

            # Safely extract predicted value
            if "predictions" in result:
                pred = result["predictions"][0]["values"][0][0]
            elif "results" in result:
                pred = result["results"][0]["values"][0][0]
            else:
                st.error("⚠️ Unexpected response format.")
                st.stop()

            st.success(f"💰 Predicted Salary: ₹{pred:,.2f}")

        except Exception as e:
            st.error("❌ Error occurred during prediction.")
            st.exception(e)
