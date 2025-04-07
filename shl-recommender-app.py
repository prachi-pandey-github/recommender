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
        try:
            api_url = "https://recommender-flask-api.onrender.com/get-recommendation"
            response = requests.get(api_url, params={"query": prompt})
            
            if response.status_code == 200:
                return response.json().get("recommendation", "No recommendation found.")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Something went wrong: {str(e)}"



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
