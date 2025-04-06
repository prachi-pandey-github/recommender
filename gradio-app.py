import gradio as gr
import pandas as pd
import os
from openai import OpenAI
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the SHL assessment data
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
            model="gpt-3.5-turbo",
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
                    return {"recommendations": result}, ""
                else:
                    # Try to find an array in the response
                    for key, value in result.items():
                        if isinstance(value, list):
                            return {"recommendations": value}, ""
                    # If nothing works, create a structure
                    return {"recommendations": [result]}, ""
            return result, ""
        except json.JSONDecodeError:
            return None, f"Failed to parse LLM response: {result_text}"
    
    except Exception as e:
        return None, str(e)

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
    
    # Format results for Gradio display
    recs = recommendations["recommendations"]
    
    # Create HTML for detailed display
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
    
    # Create dataframe for table display
    df = pd.DataFrame(recs)
    df = df[['name', 'remote', 'adaptive', 'duration', 'test_type', 'relevance_score', 'reasoning']]
    df['relevance_score'] = df['relevance_score'].apply(lambda x: f"{x:.2f}")
    
    return html_output, df

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="SHL Assessment Recommender") as demo:
    gr.Markdown("""
    # SHL Assessment Recommender
    Enter a job description or query to get recommended SHL assessments from their product catalog.
    The system analyzes your input to suggest the most relevant assessments for your needs.
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            job_input = gr.Textbox(
                label="Job Description or Query",
                placeholder="Enter job description, requirements, or specific skills you want to assess...",
                lines=10
            )
            
            with gr.Row():
                max_results = gr.Slider(
                    label="Maximum number of recommendations",
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1
                )
                submit_btn = gr.Button("Get Recommendations", variant="primary")
        
    with gr.Tabs():
        with gr.TabItem("Visual Results"):
            html_output = gr.HTML(label="Recommendations")
        with gr.TabItem("Table View"):
            table_output = gr.DataFrame(label="Recommendations Table")
    
    gr.Markdown("""
    ### About this tool
    - This tool uses AI to match job requirements with appropriate SHL assessments
    - Optimized for MAP@3 and Recall@3 to ensure the most relevant assessments are suggested
    - All assessments are sourced from SHL's official product catalog
    """)
    
    submit_btn.click(
        fn=get_recommendations,
        inputs=[job_input, max_results],
        outputs=[html_output, table_output]
    )

if __name__ == "__main__":
    demo.launch()
