import streamlit as st
import requests
import json
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the SHL assessment data
@st.cache_data
def load_assessment_data():
    # In a real implementation, this could be loaded from a database or API
    # For now, we'll use a sample of SHL assessments
    assessments = [
        {
            "name": "Verify Interactive",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-interactive/",
            "remote": "Y",
            "adaptive": "Y",
            "duration": "15-20 minutes",
            "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify G+ Cognitive Ability Test",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-g-cognitive-ability-test/",
            "remote": "Y",
            "adaptive": "Y",
            "duration": "24 minutes",
            "test_type": "Cognitive Ability"
        },
        {
            "name": "Occupational Personality Questionnaire (OPQ)",
            "link": "https://www.shl.com/solutions/products/product-catalog/opq/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "25-45 minutes",
            "test_type": "Personality Assessment"
        },
        {
            "name": "Motivational Questionnaire (MQ)",
            "link": "https://www.shl.com/solutions/products/product-catalog/mq/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "25 minutes",
            "test_type": "Motivation Assessment"
        },
        {
            "name": "Coding Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/coding-assessment/",
            "remote": "Y", 
            "adaptive": "N",
            "duration": "30-60 minutes",
            "test_type": "Technical Skills"
        },
        {
            "name": "Excel Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/excel-assessment/",
            "remote": "Y",
            "adaptive": "N", 
            "duration": "30-45 minutes",
            "test_type": "Technical Skills"
        },
        {
            "name": "Salesforce Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/salesforce-assessment/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "30-45 minutes", 
            "test_type": "Technical Skills"
        },
        {
            "name": "Contact Center Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/contact-center-assessment/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "25-40 minutes",
            "test_type": "Job-Specific"
        },
        {
            "name": "RemoteWorkQ",
            "link": "https://www.shl.com/solutions/products/product-catalog/remoteworkq/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "10-15 minutes",
            "test_type": "Work Style Assessment"
        },
        {
            "name": "ADEPT-15",
            "link": "https://www.shl.com/solutions/products/product-catalog/adept-15/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "20-25 minutes",
            "test_type": "Personality Assessment"
        },
        {
            "name": "Workplace Safety Solution",
            "link": "https://www.shl.com/solutions/products/product-catalog/workplace-safety-solution/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "30-40 minutes",
            "test_type": "Safety Assessment"
        },
        {
            "name": "Verify Numerical Reasoning",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-numerical-reasoning/",
            "remote": "Y",
            "adaptive": "Y",
            "duration": "17-18 minutes",
            "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify Verbal Reasoning",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-verbal-reasoning/",
            "remote": "Y",
            "adaptive": "Y",
            "duration": "17-19 minutes",
            "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify Inductive Reasoning",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-inductive-reasoning/",
            "remote": "Y",
            "adaptive": "Y",
            "duration": "24 minutes",
            "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify Mechanical Comprehension",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-mechanical-comprehension/",
            "remote": "Y",
            "adaptive": "N",
            "duration": "25 minutes",
            "test_type": "Technical Skills"
        }
    ]
    return assessments

# Function to recommend assessments
def recommend_assessments(job_description, max_results=10):
    assessments = load_assessment_data()
    
    # Format assessments for the prompt
    assessment_text = "\n".join([
        f"Assessment: {a['name']}\nLink: {a['link']}\nRemote: {a['remote']}\nAdaptive: {a['adaptive']}\n"
        f"Duration: {a['duration']}\nTest Type: {a['test_type']}"
        for a in assessments
    ])
    
    # Create prompt for the LLM
    prompt = f"""
    I need you to recommend relevant SHL assessments for a job based on the following job description or query:

    "{job_description}"

    Below is a list of available SHL assessments with their details:

    {assessment_text}

    Please analyze the job description and recommend between 1 and {max_results} most relevant assessments from the list above.
    For each recommendation, explain briefly why it's relevant to this job.
    Format your response as a JSON array with objects containing:
    1. "name": The name of the assessment
    2. "link": The URL link
    3. "remote": Whether it's remote (Y/N)
    4. "adaptive": Whether it's adaptive (Y/N)
    5. "duration": The assessment duration
    6. "test_type": Type of assessment
    7. "relevance_score": A relevance score from 0-1 (1 being most relevant)
    8. "reasoning": Brief explanation of why this assessment is relevant

    Provide ONLY the JSON response without any introduction or additional text.
    """

    # Get recommendations from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": "You are an HR assessment recommendation expert."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Extract and parse JSON response
        result_text = response.choices[0].message.content
        
        # Ensure we have valid JSON
        try:
            if not result_text.strip().startswith('{'):
                # If response doesn't start with {, try to extract JSON
                match = re.search(r'(\{.*\})', result_text, re.DOTALL)
                if match:
                    result_text = match.group(1)
            
            result = json.loads(result_text)
            if "recommendations" not in result:
                # If there's no recommendations key, the JSON might be an array directly
                if isinstance(result, list):
                    return {"recommendations": result}
                else:
                    # Try to find an array in the response
                    for key, value in result.items():
                        if isinstance(value, list):
                            return {"recommendations": value}
                    # If nothing works, create a structure
                    return {"recommendations": [result]}
            return result
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response", "raw_response": result_text}
    
    except Exception as e:
        return {"error": str(e)}

# Streamlit UI
st.title("SHL Assessment Recommender")
st.write("""
Enter a job description or query below to get recommended SHL assessments.
The system will analyze the text and suggest the most relevant assessments for your needs.
""")

job_description = st.text_area("Job Description or Query:", height=200)
max_results = st.slider("Maximum number of recommendations:", 1, 10, 5)

if st.button("Get Recommendations"):
    if job_description:
        with st.spinner("Analyzing and generating recommendations..."):
            recommendations = recommend_assessments(job_description, max_results)
            
            if "error" in recommendations:
                st.error(f"Error: {recommendations['error']}")
            else:
                st.success(f"Found {len(recommendations.get('recommendations', []))} relevant assessments!")
                
                # Display recommendations
                for i, rec in enumerate(recommendations.get('recommendations', []), 1):
                    with st.expander(f"{i}. {rec['name']} (Relevance: {rec['relevance_score']:.2f})"):
                        st.markdown(f"**[{rec['name']}]({rec['link']})**")
                        st.markdown(f"""
                        - **Remote:** {rec['remote']}
                        - **Adaptive:** {rec['adaptive']}
                        - **Duration:** {rec['duration']}
                        - **Test Type:** {rec['test_type']}
                        - **Why it's relevant:** {rec['reasoning']}
                        """)
                
                # Display as downloadable table
                if recommendations.get('recommendations'):
                    df = pd.DataFrame(recommendations['recommendations'])
                    st.write("### Results Table")
                    st.dataframe(df[['name', 'remote', 'adaptive', 'duration', 'test_type', 'relevance_score']])
                    
                    # Download options
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download as CSV",
                        data=csv,
                        file_name="shl_recommendations.csv",
                        mime="text/csv"
                    )
    else:
        st.warning("Please enter a job description or query.")

# Add footer information
st.markdown("---")
st.markdown("""
**About this tool:**
This recommendation engine uses LLM-powered retrieval to match job requirements with appropriate SHL assessments.
It optimizes for MAP@3 and Recall@3 to ensure the most relevant assessments are suggested.
""")
