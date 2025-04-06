import gradio as gr
import pandas as pd
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Update your .env file accordingly

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

# Load assessment data (unchanged)
def load_assessment_data():
    # ... (same as your original list of assessments)
    # [Keep your original assessments dictionary here]
    return assessments

# Recommend assessments using Gemini
def recommend_assessments(job_description, max_results=10):
    assessments = load_assessment_data()
    
    assessment_text = "\n".join([
        f"Assessment: {a['name']}\nLink: {a['link']}\nRemote: {a['remote']}\nAdaptive: {a['adaptive']}\n"
        f"Duration: {a['duration']}\nTest Type: {a['test_type']}"
        for a in assessments
    ])

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

    try:
        response = model.generate_content(prompt)
        result_text = response.text

        # Extract and parse JSON response
        try:
            match = re.search(r'(\[.*\])', result_text, re.DOTALL)
            if match:
                result_text = match.group(1)

            result = json.loads(result_text)
            return {"recommendations": result}, ""
        except json.JSONDecodeError:
            return None, f"Failed to parse Gemini response: {result_text}"

    except Exception as e:
        return None, str(e)

# Gradio function (unchanged)
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

# Gradio interface (unchanged)
with gr.Blocks(theme=gr.themes.Soft(), title="SHL Assessment Recommender") as demo:
    gr.Markdown("# SHL Assessment Recommender\nEnter a job description below to get suitable assessments.")
    with gr.Row():
        job_input = gr.Textbox(label="Job Description", lines=6, placeholder="e.g. Software Developer with strong analytical skills")
        max_results = gr.Slider(label="Max Recommendations", minimum=1, maximum=10, value=5, step=1)
    submit_btn = gr.Button("Get Recommendations")
    with gr.Row():
        output_html = gr.HTML()
        output_df = gr.Dataframe()
    submit_btn.click(get_recommendations, inputs=[job_input, max_results], outputs=[output_html, output_df])

demo.launch()
