# SHL Assignment Recommender System

This project recommends the most suitable **SHL assignment** based on a candidate’s **Job Role**, **Job Description** (skills and qualifications), and **Years of Experience**. It is built using **Streamlit** to provide an intuitive and user-friendly interface.

---

## 🧐 What It Does

Given:
- ✅ A Job Role
- ✅ A detailed Job Description (including required skills and qualifications)
- ✅ Years of Experience

The system analyzes the input and recommends the most relevant SHL assessment by using semantic similarity techniques and filters based on experience.

---

## 🌟 Features

- 🔎 Intelligent matching of job descriptions to SHL assignments
- 📊 Experience-level based filtering
- ⚡ Fast, lightweight, and interactive Streamlit UI
- 🔗 SHL API integration for real-time assignment data

---

## 📷 Screenshots

Include relevant screenshots of the application below:

![Homepage](screenshots/homepage.png)
*Homepage of the recommender system*

![Results](screenshots/results.png)
*Example of recommended SHL assignments based on input*

(You can replace the image links with actual screenshot paths in your repository.)

---

## 📁 Project Structure

```
.
├── streamlit-app.py              # Main Streamlit application
├── shl-api.py                    # Handles SHL API interaction
├── shl-recommender-app.py        # Core recommendation logic
├── requirements.txt              # Required Python libraries
├── Procfile                      # For deployment (e.g., Heroku)
└── .devcontainer/                # Optional: Dev container setup
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/prachi-pandey-github/recommender.git
cd recommender
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit App

```bash
streamlit run streamlit-app.py
```

### 4. Open in Browser

Go to `https://recommender-bdrx58rvexyfno6ujcrsvf.streamlit.app/` in your browser to interact with the app.

---

## 🎯 Use Case

Ideal for:
- **HR Professionals** looking to assign suitable SHL assessments
- **Recruiters** who want to automate the matching process
- **Hiring Platforms** integrating data-driven assessments


