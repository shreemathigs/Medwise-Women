# Medwise-Women: Patient Health and Hospital Recommendation System

![Medwise-Women Logo](https://github.com/shreemathigs/medwise-women/blob/c95586c502c39df269730eea5d0d6e90e4eeec10/assets/medwiselogo.png)

An AI-powered digital health platform designed specifically for women's healthcare needs, providing comprehensive risk assessment for **PCOS**, **thyroid disorders**, and **diabetes** with personalized doctor recommendations.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Live Demo](#-live-demo)
- [Disclaimer](#-disclaimer)
- [License](#-license)
- [Contact](#-contact)


---

## 📖 Overview

**Medwise-Women** is an innovative healthcare solution that bridges the gap between initial symptom recognition and professional medical consultation. The platform empowers women to take proactive control of their health through AI-powered risk assessment and connects them with appropriate healthcare specialists.

### 🔑 Key Highlights
- **AI-Powered Diagnostics:** Machine learning models for accurate risk prediction  
- **Personalized Recommendations:** Tailored doctor suggestions based on location and specialty  
- **Comprehensive Health Tracking:** Maintain complete health history and progress monitoring  
- **User-Friendly Interface:** Intuitive design accessible to users of all technical backgrounds  

---

## ✨ Features

### 🧠 Health Assessment
- Multi-parameter risk evaluation for PCOS, thyroid disorders, and diabetes  
- Real-time analysis of symptoms and health metrics  
- Personalized health insights and recommendations  

### 📊 BMI Calculator
- Interactive BMI calculation with visual analytics  
- Health category classification:
  - Underweight
  - Normal
  - Overweight
  - Obese  
- Progress tracking and historical data visualization  

### 🏥 Doctor Recommendation System
- Location-based specialist filtering  
- Specialty matching based on health conditions  
- Rating-based doctor ranking system  
- Comprehensive doctor profiles with contact information  

### 👩‍⚕️ Admin Dashboard
- User analytics and engagement metrics  
- Assessment statistics and disease distribution  
- System performance monitoring  
- Comprehensive reporting capabilities  

### 🔐 Security & Privacy
- Secure user authentication with password hashing  
- Encrypted data storage  
- Session management and access control  
- GDPR-compliant data handling  

---

## 📁 Project Structure

```text
medwise-women/
│
├── app.py                    # Main Streamlit application
├── database.py               # Database operations & models
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .gitignore                # Git ignore rules
│
├── assets/                   # Static assets
│   └── medwiselogo.png       # Application logo
│
├── utils/                    # Core modules
│   ├── __init__.py
│   ├── model.py              # ML prediction models
│   └── data_processor.py     # Data processing utilities
│
├── data/                     # Sample datasets
│   └── doctor_patient.csv    # Doctor database
│
└── feminine.db               # SQLite database (local)

```
---

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** – Core programming language  
- **Streamlit** – Web application framework  
- **SQLite** – Lightweight database  
- **SQLAlchemy** – Database ORM (if implemented)  

### Data Science & Machine Learning
- **Scikit-learn** – Machine learning algorithms  
- **Pandas** – Data manipulation and analysis  
- **NumPy** – Numerical computing  
- **Plotly** – Interactive visualizations  

### Frontend
- **Streamlit Components** – UI elements  
- **CSS** – Custom styling  
- **Plotly Charts** – Data visualization  

### Security
- **SHA-256** – Password hashing  
- **Session Management** – User authentication  

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher  
- pip package manager  
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/shreemathigs/medwise-women.git
cd medwise-women
```
### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```
### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
### Step 4: Run the Application
```bash
streamlit run app.py
```
### Step 5: Access the Application
```bash
http://localhost:8501
```
## 🌐 Live Demo

🚀 **Try the Medwise-Women App here:**  
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen)](https://medwise-women-6epbkmzpdjgtueoiv3ea4e.streamlit.app/)

## ⚠️ Disclaimer

This project is developed **strictly for academic and demonstration purposes**.  
All data used in this application is **dummy / synthetic data** and does **not represent real patient information**.  
The predictions and recommendations provided by this system are **not medical advice** and should **not be used for real-world diagnosis or treatment**.  

Always consult a qualified healthcare professional for medical concerns.

---
## 📜 License

This project is developed for **academic and educational purposes only**.  
All source code and materials are provided for learning and demonstration.

You may view, fork, and reference this repository for non-commercial use.  
For commercial usage or redistribution, please contact the author.

---
## 📬 Contact

**Shreemathi G.S**   

- GitHub: https://github.com/shreemathigs  
- LinkedIn: https://www.linkedin.com/in/shreemathigs/

