import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="SHL Assessment Recommender")
st.title("📊 SHL Assessment Recommender")
st.markdown("Enter role-related details and receive SHL assessment suggestions.")

role = st.text_input("Job Role")
skills = st.text_area("Key Skills (comma separated)")
experience = st.slider("Years of Experience", 0, 30, 3)

def get_recommendations(prompt):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": os.getenv("GEMINI_API_KEY")}  # or replace with your actual key for testing
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code == 200:
        reply = response.json()
        return reply["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
if st.button("Get Recommendations"):
    if role and skills:
        prompt = f"Suggest suitable SHL assessments for a candidate applying as a {role} with {experience} years of experience and skills in {skills}."
        with st.spinner("Generating recommendations..."):
            recommendations = get_recommendations(prompt)
        st.subheader("Recommended SHL Assessments:")
        st.write(recommendations)
    else:
        st.warning("Please fill in all the fields.")
