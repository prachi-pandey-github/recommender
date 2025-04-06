import gradio as gr
import pandas as pd
import os
import openai
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the SHL assessment data
def load_assessment_data():
    return [
        {
            "name": "Verify Interactive",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-interactive/",
            "remote": "Y", "adaptive": "Y", "duration": "15-20 minutes", "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify G+ Cognitive Ability Test",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-g-cognitive-ability-test/",
            "remote": "Y", "adaptive": "Y", "duration": "24 minutes", "test_type": "Cognitive Ability"
        },
        {
            "name": "Occupational Personality Questionnaire (OPQ)",
            "link": "https://www.shl.com/solutions/products/product-catalog/opq/",
            "remote": "Y", "adaptive": "N", "duration": "25-45 minutes", "test_type": "Personality Assessment"
        },
        {
            "name": "Motivational Questionnaire (MQ)",
            "link": "https://www.shl.com/solutions/products/product-catalog/mq/",
            "remote": "Y", "adaptive": "N", "duration": "25 minutes", "test_type": "Motivation Assessment"
        },
        {
            "name": "Coding Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/coding-assessment/",
            "remote": "Y", "adaptive": "N", "duration": "30-60 minutes", "test_type": "Technical Skills"
        },
        {
            "name": "Excel Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/excel-assessment/",
            "remote": "Y", "adaptive": "N", "duration": "30-45 minutes", "test_type": "Technical Skills"
        },
        {
            "name": "Salesforce Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/salesforce-assessment/",
            "remote": "Y", "adaptive": "N", "duration": "30-45 minutes", "test_type": "Technical Skills"
        },
        {
            "name": "Contact Center Assessment",
            "link": "https://www.shl.com/solutions/products/product-catalog/contact-center-assessment/",
            "remote": "Y", "adaptive": "N", "duration": "25-40 minutes", "test_type": "Job-Specific"
        },
        {
            "name": "RemoteWorkQ",
            "link": "https://www.shl.com/solutions/products/product-catalog/remoteworkq/",
            "remote": "Y", "adaptive": "N", "duration": "10-15 minutes", "test_type": "Work Style Assessment"
        },
        {
            "name": "ADEPT-15",
            "link": "https://www.shl.com/solutions/products/product-catalog/adept-15/",
            "remote": "Y", "adaptive": "N", "duration": "20-25 minutes", "test_type": "Personality Assessment"
        },
        {
            "name": "Workplace Safety Solution",
            "link": "https://www.shl.com/solutions/products/product-catalog/workplace-safety-solution/",
            "remote": "Y", "adaptive": "N", "duration": "30-40 minutes", "test_type": "Safety Assessment"
        },
        {
            "name": "Verify Numerical Reasoning",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-numerical-reasoning/",
            "remote": "Y", "adaptive": "Y", "duration": "17-18 minutes", "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify Verbal Reasoning",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-verbal-reasoning/",
            "remote": "Y", "adaptive": "Y", "duration": "17-19 minutes", "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify Inductive Reasoning",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-inductive-reasoning/",
            "remote": "Y", "adaptive": "Y", "duration": "24 minutes", "test_type": "Cognitive Ability"
        },
        {
            "name": "Verify Mechanical Comprehension",
            "link": "https://www.shl.com/solutions/products/product-catalog/verify-mechanical-comprehension/",
            "remote": "Y", "adaptive": "N", "duration": "25 minutes", "test_type": "Technical Skills"
        }
    ]

# Function to recommend assessments using GPT
def recommend_assessments(job_description, max_results=10):
    assessments = load_assessment_data()
    assessment_text = "\n".join([
        f"Assessment: {a['name']}\nLink: {a['link']}\nRemote: {a['remote']}\nAdaptive: {a['adaptive']}\n"
        f"Duration: {a['duration']}\nTest Type: {a['test_type']}" for a in assessments
    ])
    
    prompt = f"""
    I need you to recommend relevant SHL assessments for a job based on the following job description or query:

    "{job_description}"

    Below is a list of available SHL assessments with their details:

    {assessment_text}

    Please analyze the job description and recommend between 1 and {max_results} most relevant assessments.
    Format your response as a JSON array with objects containing:
    "name", "link", "remote", "adaptive", "duration", "test_type", "relevance_score", "reasoning"
    Only respond with the JSON.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an HR assessment recommendation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        result_text = response['choices'][0]['message']['content']

        # Try to find the JSON structure
        match = re.search(r'(\[.*\])', result_text, re.DOTALL)
        if match:
            json_data = match.group(1)
            result = json.loads(json_data)
            return {"recommendations": result}, ""

        return None, "Could not extract JSON from LLM response."

    except Exception as e:
        return None, f"Error from OpenAI: {str(e)}"

# Gradio interface function
def get_recommendations(job_description, max_results):
    if not job_description.strip():
        return None, "Please provide a job description or query."

    max_results = int(max_results)
    recommendations, error = recommend_assessments(job_description, max_results)

    if error:
        return None, error
    if not recommendations or "recommendations" not in recommendations:
        return None, "No recommendations could be generated."

    recs = recommendations["recommendations"]
    html_output = "<div style='max-width:800px'>"

    for i, rec in enumerate(recs, 1):
        relevance = round(rec["relevance_score"] * 100)
        relevance_bar = f"<div style='width:100%; background:#eee'><div style='width:{relevance}%; background:linear-gradient(90deg, #2a4365 0%, #4299e1 100%); color:white; padding:3px 6px'>{relevance}%</div></div>"

        html_output += f"""
        <div style='margin-bottom:20px; padding:15px; border:1px solid #ddd; border-radius:8px'>
            <h3 style='margin-top:0'>
                {i}. <a href="{rec['link']}" target="_blank" style='color:#2b6cb0'>{rec['name']}</a>
            </h3>
            <p><strong>Relevance:</strong> {relevance_bar}</p>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px'>
                <div><strong>Remote:</strong> {rec['remote']}</div>
                <div><strong>Adaptive:</strong> {rec['adaptive']}</div>
                <div><strong>Duration:</strong> {rec['duration']}</div>
                <div><strong>Test Type:</strong> {rec['test_type']}</div>
            </div>
            <p><strong>Why it's relevant:</strong> {rec['reasoning']}</p>
        </div>
        """
    html_output += "</div>"

    df = pd.DataFrame(recs)
    df = df[['name', 'remote', 'adaptive', 'duration', 'test_type', 'relevance_score', 'reasoning']]
    df['relevance_score'] = df['relevance_score'].apply(lambda x: f"{x:.2f}")
    
    return html_output, df

# Gradio app
with gr.Blocks(theme=gr.themes.Soft(), title="SHL Assessment Recommender") as demo:
    gr.Markdown("## 🔍 SHL Assessment Recommender\nEnter a job description and get smart suggestions for relevant SHL assessments.")

    with gr.Row():
        job_desc = gr.Textbox(label="Job Description", placeholder="Enter job description...", lines=6)
        max_results = gr.Number(label="Max Assessments to Recommend", value=5, precision=0)

    with gr.Row():
        btn = gr.Button("Recommend Assessments")
    
    output_html = gr.HTML()
    output_df = gr.Dataframe(interactive=False)

    btn.click(fn=get_recommendations, inputs=[job_desc, max_results], outputs=[output_html, output_df])

# Launch the app
demo.launch()
