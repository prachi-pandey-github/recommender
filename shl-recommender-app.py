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
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp-01-21:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": os.getenv("GEMINI_API_KEY")}  # or replace with actual key during testing
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code == 200:
        reply = response.json()
        try:
            return reply["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "No valid response received from Gemini."
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
