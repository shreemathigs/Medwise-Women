import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.model import HealthPredictor
from utils.data_processor import DataProcessor
from database import db
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Medwise-Women: Patient Health & Hospital Recommendation System",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #e91e63;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #ad1457;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .tagline {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .risk-low {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        color: #2e7d32;
    }
    .risk-medium {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        color: #ef6c00;
    }
    .risk-high {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        color: #c62828;
    }
    .doctor-card {
        background-color: #fce4ec;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #e91e63;
        color: #333;
    }
    .doctor-card h4 {
        color: #ad1457;
        margin-bottom: 10px;
    }
    .doctor-card p {
        color: #555;
        margin: 5px 0;
    }
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Reference Range Cards */
    .range-card {
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid;
    }
    .bmi-range {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
        color: #1b5e20;
    }
    .tsh-range {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
        color: #0d47a1;
    }
    .sugar-range {
        background-color: #fff3e0;
        border-left-color: #ff9800;
        color: #e65100;
    }
    .bp-range {
        background-color: #fce4ec;
        border-left-color: #e91e63;
        color: #880e4f;
    }
    .range-card h4 {
        margin-bottom: 15px;
        font-size: 1.2rem;
    }
    .range-card ul {
        margin-left: 15px;
    }
    .range-card li {
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    
    /* BMI Calculator Card */
    .bmi-calculator-card {
        background-color: #e3f2fd;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #1976d2;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: #0d47a1;
    }
    .bmi-calculator-card h3 {
        color: #1565c0;
        margin-bottom: 10px;
    }
    .bmi-calculator-card p {
        color: #1976d2;
        margin: 0;
    }
    
    /* Health Implications Card */
    .health-implications-card {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        margin: 15px 0;
        color: #e65100;
    }
    .health-implications-card h4 {
        color: #ef6c00;
        margin-bottom: 15px;
    }
    .health-implications-card p {
        color: #e65100;
        margin-bottom: 10px;
    }
    .health-implications-card ul {
        color: #e65100;
        margin-left: 15px;
    }
    
    /* Health Tips Card */
    .health-notes-card {
        background-color: #f3e5f5;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #7b1fa2;
        margin: 15px 0;
        color: #4a148c;
    }
    .health-notes-card h4 {
        color: #6a1b9a;
        margin-bottom: 15px;
    }
    .health-notes-card ul {
        color: #4a148c;
        margin-left: 15px;
    }
    .health-notes-card li {
        margin-bottom: 8px;
    }
    
    /* Sidebar Navigation Styles */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #fafafa;
    }
    .st-emotion-cache-16idsys p {
        color: #666666 !important;
        font-weight: 500;
    }
    .st-emotion-cache-1y4p8pa h2 {
        color: #e91e63 !important;
    }
    .st-emotion-cache-1v7f65g p {
        color: #555555 !important;
        font-weight: 500;
    }
    .st-emotion-cache-1v7f65g p:hover {
        color: #e91e63 !important;
    }
    div[data-testid="stSidebar"] p {
        color: #666666;
    }
    div[data-testid="stSidebar"] h2 {
        color: #e91e63;
    }
    
    /* Image styling */
    .homepage-image {
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .logo-image {
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

class MedwiseApp:
    def __init__(self):
        # Initialize ALL session state variables FIRST
        self.initialize_session_state()
        
        self.predictor = HealthPredictor()
        self.processor = DataProcessor()
        load_css()
        
    def initialize_session_state(self):
        """Initialize all session state variables to prevent data loss"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'assessment_history' not in st.session_state:
            st.session_state.assessment_history = []
        if 'doctors' not in st.session_state:
            st.session_state.doctors = []
        if 'last_assessment' not in st.session_state:
            st.session_state.last_assessment = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Home"
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'name': '', 'age': 25, 'bmi': 22.0, 'tsh_level': 2.5, 'blood_sugar': 100,
                'irregular_periods': False, 'excess_hair_growth': False, 'acne': False,
                'tiredness': False, 'hair_fall': False, 'frequent_urination': False,
                'family_pcos': False, 'family_thyroid': False, 'family_diabetes': False
            }
        
    def run(self):
        # Show login if not authenticated
        if not st.session_state.authenticated:
            self.login_page()
            return
        
        # Main app navigation
        with st.sidebar:
            # Display small logo only in sidebar
            self.display_logo()
            
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <h2 style='color: #e91e63;'>❤️ Medwise-Women</h2>
                <p style='color: #666;'>Welcome, {st.session_state.current_user}!</p>
            </div>
            """, unsafe_allow_html=True)
            
            selected = option_menu(
                "Navigation Menu",
                ["Home", "Reference Ranges", "Health Assessment", "BMI Calculator", "Doctor Recommendations", "Health History", "Disease Information", "Logout"],
                icons=['house', 'clipboard-data', 'clipboard-pulse', 'calculator', 'person-badge', 'clock-history', 'info-circle', 'box-arrow-right'],
                menu_icon="heart-pulse",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "#fafafa"},
                    "icon": {"color": "#e91e63", "font-size": "20px"},
                    "nav-link": {
                        "font-size": "16px", 
                        "text-align": "left", 
                        "margin": "0px", 
                        "--hover-color": "#fce4ec",
                        "color": "#555555"
                    },
                    "nav-link-selected": {
                        "background-color": "#e91e63",
                        "color": "white"
                    },
                }
            )
            
            if selected == "Logout":
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.session_state.assessment_history = []
                st.rerun()
            
            # Update current page in session state
            st.session_state.current_page = selected
        
        # Route to the selected page
        if st.session_state.current_page == "Home":
            self.home_page()
        elif st.session_state.current_page == "Reference Ranges":
            self.reference_ranges_page()
        elif st.session_state.current_page == "Health Assessment":
            self.assessment_page()
        elif st.session_state.current_page == "BMI Calculator":
            self.bmi_calculator_page()
        elif st.session_state.current_page == "Doctor Recommendations":
            self.doctor_recommendations_page()
        elif st.session_state.current_page == "Health History":
            self.history_page()
        elif st.session_state.current_page == "Disease Information":
            self.disease_info_page()

    def display_logo(self):
        """Display the Medwise logo only in sidebar"""
        logo_paths = [
            "assets/medwiselogo.png",
            "assets/medwiselogo.jpg",
            "assets/medwiselogo.jpeg",
            "images/medwiselogo.png",
            "medwiselogo.png"
        ]
        
        logo_found = False
        for logo_path in logo_paths:
            try:
                st.image(logo_path, 
                        use_container_width=True,
                        output_format="auto")
                logo_found = True
                break
            except:
                continue
        
        if not logo_found:
            # Display small placeholder if logo not found
            st.markdown("""
            <div style='background: #f0f8ff; padding: 10px; border-radius: 10px; text-align: center; border: 2px dashed #e91e63; margin-bottom: 20px;'>
                <h4 style='color: #e91e63; margin: 0;'>Medwise</h4>
            </div>
            """, unsafe_allow_html=True)

    def login_page(self):
        st.markdown('<div class="main-header">Medwise-Women</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-header">Patient Health & Hospital Recommendation System</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Login to Your Account")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login", type="primary")
                
                if login_btn:
                    if username and password:
                        if db.authenticate_user(username, password):
                            st.session_state.authenticated = True
                            st.session_state.current_user = username
                            st.session_state.assessment_history = db.get_user_assessments(username)
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.error("⚠️ Please enter both username and password")
        
        with tab2:
            with st.form("signup_form"):
                st.subheader("Create New Account")
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email (optional)")
                signup_btn = st.form_submit_button("Sign Up", type="primary")
                
                if signup_btn:
                    if not new_username or not new_password:
                        st.error("⚠️ Please fill all required fields")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif len(new_username) < 3:
                        st.error("❌ Username must be at least 3 characters long")
                    elif db.user_exists(new_username):
                        st.error("❌ Username already exists!")
                    else:
                        if db.create_user(new_username, new_password, email):
                            st.session_state.authenticated = True
                            st.session_state.current_user = new_username
                            st.session_state.assessment_history = []
                            st.success("🎉 Account created successfully! You are now logged in.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create account. Please try again.")
        
        # Demo credentials info
        st.markdown("---")
        st.info("""
        **Demo Credentials:**
        - Username: `demo` | Password: `demo123`
        - Username: `test` | Password: `test123`
        - Username: `admin` | Password: `admin123`
        """)

    def home_page(self):
        st.markdown('<div class="main-header">Medwise-Women</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Patient Health & Hospital Recommendation System</div>', unsafe_allow_html=True)
        st.markdown('<div class="tagline">Empowering Women\'s Health Through AI</div>', unsafe_allow_html=True)
    
       
        col1, col2 = st.columns([2, 1])
    
        with col1:
            st.markdown("""
            ### Welcome to Your Personal Health Companion
        
            Medwise-Women helps you assess your risk for common women's health conditions 
            and connects you with the right specialists for your needs.
        
            **Key Features:**
            - 🩺 AI-powered health risk assessment
            - 📊 BMI Calculator & Health Metrics
            - 🏥 Personalized doctor recommendations
            - 💡 Prevention tips and exercises
            - 📈 Health history tracking
            - 🎯 Condition-specific guidance
            """)
        
            # Simple instruction instead of button
            st.markdown("---")
            st.info("💡 **Get Started**: Use the sidebar navigation on the left to access Health Assessment and other features!")
    
        with col2:
            # Health stats or quick info
            st.markdown("""
            <div style='background: #e8f5e9; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                <h4 style='color: #2e7d32; text-align: center;'>📈 Health Stats</h4>
                <p style='text-align: center; color: #555; margin: 0;'>
                    Regular health assessments can help in early detection and prevention of diseases.
                </p>
            </div>
            """, unsafe_allow_html=True)


            
    def reference_ranges_page(self):
        st.markdown('<div class="main-header">Reference Ranges</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Normal Health Parameter Ranges</div>', unsafe_allow_html=True)
        
        st.info("📋 Use these reference ranges to understand your health parameters and compare with your assessment results.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="range-card bmi-range">
                <h4>📏 BMI Categories</h4>
                <ul>
                <li><strong>Underweight:</strong> Below 18.5</li>
                <li><strong>Normal weight:</strong> 18.5 - 24.9</li>
                <li><strong>Overweight:</strong> 25 - 29.9</li>
                <li><strong>Obese:</strong> 30 and above</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="range-card sugar-range">
                <h4>🩸 Blood Sugar Levels</h4>
                <ul>
                <li><strong>Fasting Normal:</strong> 70 - 100 mg/dL</li>
                <li><strong>Pre-diabetes:</strong> 100 - 125 mg/dL</li>
                <li><strong>Diabetes:</strong> 126 mg/dL and above</li>
                <li><strong>Post-meal (2hr):</strong> Below 140 mg/dL</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="range-card tsh-range">
                <h4>🦋 TSH Levels</h4>
                <ul>
                <li><strong>Normal Range:</strong> 0.4 - 4.0 mIU/L</li>
                <li><strong>Below 0.4:</strong> Possible hyperthyroidism</li>
                <li><strong>Above 4.0:</strong> Possible hypothyroidism</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="range-card bp-range">
                <h4>💓 Blood Pressure</h4>
                <ul>
                <li><strong>Normal:</strong> Below 120/80 mmHg</li>
                <li><strong>Elevated:</strong> 120-129/80 mmHg</li>
                <li><strong>High Stage 1:</strong> 130-139/80-89 mmHg</li>
                <li><strong>High Stage 2:</strong> 140+/90+ mmHg</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    def assessment_page(self):
        st.markdown('<div class="main-header">Health Risk Assessment</div>', unsafe_allow_html=True)
        
        st.info("🔍 Compare your results with normal ranges in the 'Reference Ranges' section for better understanding.")
        
        # Quick reference cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid #4caf50;'>
                <h4 style='color: #2e7d32; margin: 0;'>📏 BMI Range</h4>
                <p style='color: #555; margin: 5px 0 0 0;'>Normal: 18.5 - 24.9</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 4px solid #2196f3;'>
                <h4 style='color: #1565c0; margin: 0;'>🦋 TSH Range</h4>
                <p style='color: #555; margin: 5px 0 0 0;'>Normal: 0.4 - 4.0 mIU/L</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: #fff3e0; padding: 15px; border-radius: 10px; border-left: 4px solid #ff9800;'>
                <h4 style='color: #ef6c00; margin: 0;'>🩸 Sugar Range</h4>
                <p style='color: #555; margin: 5px 0 0 0;'>Normal: 70 - 100 mg/dL</p>
            </div>
            """, unsafe_allow_html=True)
        
        form_data = st.session_state.form_data
        
        with st.form("health_assessment"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Personal Information")
                name = st.text_input("Full Name", value=form_data['name'] or st.session_state.current_user)
                age = st.number_input("Age", min_value=10, max_value=100, value=form_data['age'])
                bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=form_data['bmi'], step=0.1)
                tsh_level = st.number_input("TSH Level (mIU/L)", min_value=0.0, max_value=10.0, value=form_data['tsh_level'], step=0.1)
                blood_sugar = st.number_input("Blood Sugar (mg/dL)", min_value=50, max_value=300, value=form_data['blood_sugar'])
            
            with col2:
                st.subheader("Symptoms")
                irregular_periods = st.checkbox("Irregular Periods", value=form_data['irregular_periods'])
                excess_hair_growth = st.checkbox("Excess Hair Growth", value=form_data['excess_hair_growth'])
                acne = st.checkbox("Acne", value=form_data['acne'])
                tiredness = st.checkbox("Tiredness/Fatigue", value=form_data['tiredness'])
                hair_fall = st.checkbox("Hair Fall", value=form_data['hair_fall'])
                frequent_urination = st.checkbox("Frequent Urination", value=form_data['frequent_urination'])
                
                st.subheader("Family History")
                family_pcos = st.checkbox("Family History of PCOS", value=form_data['family_pcos'])
                family_thyroid = st.checkbox("Family History of Thyroid", value=form_data['family_thyroid'])
                family_diabetes = st.checkbox("Family History of Diabetes", value=form_data['family_diabetes'])
            
            submitted = st.form_submit_button("Assess My Health", type="primary")
            
            if submitted:
                st.session_state.form_data = {
                    'name': name, 'age': age, 'bmi': bmi, 'tsh_level': tsh_level, 'blood_sugar': blood_sugar,
                    'irregular_periods': irregular_periods, 'excess_hair_growth': excess_hair_growth, 'acne': acne,
                    'tiredness': tiredness, 'hair_fall': hair_fall, 'frequent_urination': frequent_urination,
                    'family_pcos': family_pcos, 'family_thyroid': family_thyroid, 'family_diabetes': family_diabetes
                }
                
                self.process_assessment(name, age, bmi, tsh_level, blood_sugar, irregular_periods, 
                                      excess_hair_growth, acne, tiredness, hair_fall, frequent_urination, 
                                      family_pcos, family_thyroid, family_diabetes)
        
        if st.session_state.last_assessment:
            st.markdown("---")
            st.subheader("📋 Last Assessment Results")
            self.display_previous_results(st.session_state.last_assessment)

    def bmi_calculator_page(self):
        st.markdown('<div class="main-header">BMI Calculator</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="bmi-calculator-card">
                <h3>📊 BMI Calculator</h3>
                <p>Calculate your Body Mass Index (BMI) to understand your weight category and health risks.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("bmi_calculator"):
                st.subheader("Calculate Your BMI")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    height_unit = st.radio("Height Unit", ["cm", "feet"], horizontal=True)
                    if height_unit == "cm":
                        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=165)
                    else:
                        col_feet, col_inches = st.columns(2)
                        with col_feet:
                            feet = st.number_input("Feet", min_value=4, max_value=7, value=5)
                        with col_inches:
                            inches = st.number_input("Inches", min_value=0, max_value=11, value=5)
                        height = (feet * 12 + inches) * 2.54
                        st.write(f"Height: {height:.1f} cm")
                
                with col_b:
                    weight_unit = st.radio("Weight Unit", ["kg", "lbs"], horizontal=True)
                    weight = st.number_input(f"Weight ({weight_unit})", min_value=30.0, max_value=200.0, value=60.0, step=0.1)
                
                calculate_bmi = st.form_submit_button("Calculate BMI", type="primary", use_container_width=True)
                
                if calculate_bmi:
                    if weight_unit == "lbs":
                        weight_kg = weight * 0.453592
                    else:
                        weight_kg = weight
                    
                    height_m = height / 100
                    bmi = weight_kg / (height_m ** 2)
                    
                    if bmi < 18.5:
                        category = "Underweight"
                        color = "#2196f3"
                        advice = "Consider consulting a nutritionist for healthy weight gain"
                    elif bmi < 25:
                        category = "Normal weight"
                        color = "#4caf50"
                        advice = "Maintain your healthy lifestyle with balanced diet and exercise"
                    elif bmi < 30:
                        category = "Overweight"
                        color = "#ff9800"
                        advice = "Consider lifestyle modifications for weight management"
                    else:
                        category = "Obese"
                        color = "#f44336"
                        advice = "Consult healthcare provider for comprehensive weight management"
                    
                    st.success(f"**Your BMI: {bmi:.1f}**")
                    st.markdown(f"""
                    <div style='background-color: {color}20; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; margin: 15px 0;'>
                        <h4 style='color: {color}; margin: 0 0 10px 0;'>Category: {category}</h4>
                        <p style='color: #555; margin: 0;'>{advice}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="range-card bmi-range">
                <h4>📏 BMI Reference</h4>
                <ul>
                <li><strong>Underweight:</strong> < 18.5</li>
                <li><strong>Normal:</strong> 18.5 - 24.9</li>
                <li><strong>Overweight:</strong> 25 - 29.9</li>
                <li><strong>Obese:</strong> ≥ 30</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="health-implications-card">
                <h4>🏥 Health Implications</h4>
                <p><strong>High BMI may increase risk of:</strong></p>
                <ul>
                <li>Heart disease</li>
                <li>Diabetes</li>
                <li>High blood pressure</li>
                <li>Certain cancers</li>
                </ul>
                <p><strong>Low BMI may indicate:</strong></p>
                <ul>
                <li>Nutritional deficiencies</li>
                <li>Weakened immune system</li>
                <li>Osteoporosis risk</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    def doctor_recommendations_page(self):
        st.markdown('<div class="main-header">Find Specialists & Hospitals</div>', unsafe_allow_html=True)
        
        all_specialties = ['All'] + db.get_all_specialties()
        all_locations = ['All'] + db.get_all_locations()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            specialty = st.selectbox("Specialty", all_specialties)
        
        with col2:
            location = st.selectbox("Location", all_locations)
        
        with col3:
            st.write("")
            search_btn = st.button("🔍 Search Doctors", type="primary", use_container_width=True)
        
        if search_btn:
            doctors_data = db.get_doctors_by_specialty(specialty, location)
            st.session_state.doctors = doctors_data
        
        if st.session_state.doctors:
            st.subheader(f"👩‍⚕️ Found {len(st.session_state.doctors)} Doctor(s)")
            
            for doctor in st.session_state.doctors:
                rating = doctor['rating']
                rating_color = "#4caf50" if rating >= 4.5 else "#ff9800" if rating >= 4.0 else "#f44336"
                
                st.markdown(f"""
                <div class="doctor-card">
                    <h4>👩‍⚕️ {doctor['name']}</h4>
                    <p><strong>Specialty:</strong> {doctor['specialty']}</p>
                    <p><strong>Hospital:</strong> {doctor['hospital']}, {doctor['location']}</p>
                    <p><strong>Rating:</strong> <span style='color: {rating_color}; font-weight: bold;'>{rating}/5 ⭐</span></p>
                    <p><strong>Contact:</strong> {doctor['contact']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            if not search_btn:
                st.info("👆 Use the filters above to search for doctors")
            else:
                st.warning("No doctors found matching your criteria. Try adjusting your filters.")

    def history_page(self):
        st.markdown('<div class="main-header">Your Health History</div>', unsafe_allow_html=True)
        
        assessments = db.get_user_assessments(st.session_state.current_user)
        
        if assessments:
            st.success(f"📊 You have {len(assessments)} assessment(s) in your history")
            for i, assessment in enumerate(assessments):
                with st.expander(f"Assessment {i+1} - {assessment['timestamp']}", expanded=i==0):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Name:** {assessment['name']}")
                        st.write(f"**Date:** {assessment['timestamp']}")
                        st.write(f"**Overall Risk:** {assessment['overall_risk']}")
                        if 'disease_diagnosis' in assessment:
                            st.write(f"**Primary Diagnosis:** {assessment['disease_diagnosis']['primary_disease']}")
                            st.write(f"**Confidence:** {assessment['disease_diagnosis']['confidence']:.1f}%")
                    
                    with col2:
                        risks = assessment['predictions']
                        st.write("**Risk Breakdown:**")
                        st.write(f"- PCOS: {risks.get('pcos_risk', 0)*100:.1f}%")
                        st.write(f"- Thyroid: {risks.get('thyroid_risk', 0)*100:.1f}%")
                        st.write(f"- Diabetes: {risks.get('diabetes_risk', 0)*100:.1f}%")
                    
                    if st.button(f"View Full Report", key=f"view_{i}"):
                        self.display_results(assessment['predictions'], assessment['name'], assessment['input_data'])
        else:
            st.info("No assessment history found. Complete a health assessment to see your history here.")

    def disease_info_page(self):
        st.markdown('<div class="main-header">Women\'s Health Information</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🎀 PCOS", "🦋 Thyroid Disorders", "🩺 Diabetes"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background: #f3e5f5; padding: 20px; border-radius: 10px; border-left: 4px solid #9c27b0;'>
                <h3 style='color: #7b1fa2;'>Symptoms</h3>
                <ul style='color: #555;'>
                <li>Irregular menstrual cycles</li>
                <li>Excess hair growth</li>
                <li>Acne and oily skin</li>
                <li>Weight gain</li>
                <li>Difficulty getting pregnant</li>
                <li>Hair loss from head</li>
                <li>Darkening of skin</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 4px solid #4caf50;'>
                <h3 style='color: #2e7d32;'>Management</h3>
                <ul style='color: #555;'>
                <li>Lifestyle changes (diet & exercise)</li>
                <li>Medications to regulate periods</li>
                <li>Fertility treatments if needed</li>
                <li>Anti-androgen medications</li>
                <li>Regular monitoring</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 4px solid #2196f3;'>
                <h3 style='color: #1565c0;'>Symptoms (Hypothyroidism)</h3>
                <ul style='color: #555;'>
                <li>Fatigue and weakness</li>
                <li>Weight gain</li>
                <li>Depression</li>
                <li>Hair loss</li>
                <li>Cold intolerance</li>
                <li>Constipation</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: #fff3e0; padding: 20px; border-radius: 10px; border-left: 4px solid #ff9800;'>
                <h3 style='color: #ef6c00;'>Management</h3>
                <ul style='color: #555;'>
                <li>Thyroid hormone replacement</li>
                <li>Regular TSH monitoring</li>
                <li>Balanced diet with iodine</li>
                <li>Stress management</li>
                <li>Regular exercise</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background: #ffebee; padding: 20px; border-radius: 10px; border-left: 4px solid #f44336;'>
                <h3 style='color: #c62828;'>Symptoms</h3>
                <ul style='color: #555;'>
                <li>Increased thirst and hunger</li>
                <li>Frequent urination</li>
                <li>Unexplained weight loss</li>
                <li>Fatigue</li>
                <li>Blurred vision</li>
                <li>Slow healing wounds</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 4px solid #4caf50;'>
                <h3 style='color: #2e7d32;'>Management</h3>
                <ul style='color: #555;'>
                <li>Blood sugar monitoring</li>
                <li>Healthy diet</li>
                <li>Regular exercise</li>
                <li>Medications/Insulin</li>
                <li>Regular check-ups</li>
                <li>Foot care</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

    def process_assessment(self, name, age, bmi, tsh_level, blood_sugar, 
                          irregular_periods, excess_hair_growth, acne, tiredness,
                          hair_fall, frequent_urination, family_pcos, family_thyroid,
                          family_diabetes):
        
        with st.spinner("Analyzing your health data..."):
            input_data = {
                'Age': age, 'BMI': bmi, 'Irregular_Periods': int(irregular_periods),
                'Excess_Hair_Growth': int(excess_hair_growth), 'Acne': int(acne),
                'TSH_Level': tsh_level, 'Tiredness': int(tiredness), 'Hair_Fall': int(hair_fall),
                'Blood_Sugar': blood_sugar, 'Frequent_Urination': int(frequent_urination),
                'Family_Diabetes': int(family_diabetes)
            }
            
            predictions = self.predictor.predict(input_data)
            
            assessment_data = {
                'name': name, 'predictions': predictions, 'input_data': input_data,
                'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                'overall_risk': self.calculate_overall_risk(predictions),
                'disease_diagnosis': self.get_disease_diagnosis(predictions, input_data)
            }
            
            st.session_state.last_assessment = assessment_data
            st.session_state.assessment_history.append(assessment_data)
            db.save_assessment(st.session_state.current_user, assessment_data)
            
            self.display_results(predictions, name, input_data)

    def display_previous_results(self, assessment):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {assessment['name']}")
            st.write(f"**Date:** {assessment['timestamp']}")
            st.write(f"**Overall Risk:** {assessment['overall_risk']}")
        
        with col2:
            risks = assessment['predictions']
            st.write("**Risk Breakdown:**")
            st.write(f"- PCOS: {risks.get('pcos_risk', 0)*100:.1f}%")
            st.write(f"- Thyroid: {risks.get('thyroid_risk', 0)*100:.1f}%")
            st.write(f"- Diabetes: {risks.get('diabetes_risk', 0)*100:.1f}%")
        
        if st.button("View Full Details"):
            self.display_results(assessment['predictions'], assessment['name'], assessment['input_data'])

    def get_disease_diagnosis(self, predictions, input_data):
        diagnosis = {
            'primary_disease': None, 'confidence': 0, 'symptoms_matched': [], 'recommendations': []
        }
        
        pcos_score = 0
        thyroid_score = 0
        diabetes_score = 0
        
        if input_data['Irregular_Periods']:
            pcos_score += 3
            diagnosis['symptoms_matched'].append("Irregular Periods - Strong indicator of PCOS")
        if input_data['Excess_Hair_Growth']:
            pcos_score += 2
            diagnosis['symptoms_matched'].append("Excess Hair Growth - Common in PCOS")
        if input_data['Acne']:
            pcos_score += 1
            diagnosis['symptoms_matched'].append("Acne - Can be related to PCOS")
        
        if input_data['TSH_Level'] < 0.4 or input_data['TSH_Level'] > 4.0:
            thyroid_score += 3
            diagnosis['symptoms_matched'].append(f"TSH Level {input_data['TSH_Level']} - Outside normal range (0.4-4.0)")
        if input_data['Tiredness']:
            thyroid_score += 2
            diagnosis['symptoms_matched'].append("Fatigue - Common thyroid symptom")
        if input_data['Hair_Fall']:
            thyroid_score += 1
            diagnosis['symptoms_matched'].append("Hair Fall - Thyroid-related symptom")
        
        if input_data['Blood_Sugar'] > 126:
            diabetes_score += 3
            diagnosis['symptoms_matched'].append(f"Blood Sugar {input_data['Blood_Sugar']} mg/dL - High (Normal: <100 mg/dL)")
        if input_data['Frequent_Urination']:
            diabetes_score += 2
            diagnosis['symptoms_matched'].append("Frequent Urination - Classic diabetes symptom")
        if input_data['Family_Diabetes']:
            diabetes_score += 1
            diagnosis['symptoms_matched'].append("Family History of Diabetes - Increases risk")
        
        scores = {
            'PCOS': pcos_score + predictions['pcos_risk'] * 10,
            'Thyroid': thyroid_score + predictions['thyroid_risk'] * 10,
            'Diabetes': diabetes_score + predictions['diabetes_risk'] * 10
        }
        
        diagnosis['primary_disease'] = max(scores, key=scores.get)
        diagnosis['confidence'] = scores[diagnosis['primary_disease']] / 13 * 100
        
        if diagnosis['primary_disease'] == 'PCOS':
            diagnosis['recommendations'] = [
                "Consult a Gynecologist for proper diagnosis",
                "Consider lifestyle changes including diet and exercise",
                "Monitor menstrual cycles regularly"
            ]
        elif diagnosis['primary_disease'] == 'Thyroid':
            diagnosis['recommendations'] = [
                "Consult an Endocrinologist for TSH level evaluation",
                "Regular thyroid function tests recommended",
                "Discuss medication options if needed"
            ]
        else:
            diagnosis['recommendations'] = [
                "Consult a Diabetologist for blood sugar management",
                "Monitor blood glucose levels regularly",
                "Follow a diabetic diet and exercise regimen"
            ]
        
        return diagnosis

    def display_results(self, predictions, name, input_data):
        st.success("🎉 Assessment Complete!")
        
        overall_risk = self.calculate_overall_risk(predictions)
        risk_class = "risk-high" if overall_risk == "High" else "risk-medium" if overall_risk == "Medium" else "risk-low"
        
        st.markdown(f"""
        <div class="{risk_class}">
            <h3>Overall Health Risk: {overall_risk}</h3>
            <p>Based on your inputs, we've assessed your risk for common women's health conditions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        diagnosis = self.get_disease_diagnosis(predictions, input_data)
        
        st.subheader("🔍 Disease Diagnosis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Most Likely Condition:** {diagnosis['primary_disease']}
            **Confidence Level:** {diagnosis['confidence']:.1f}%
            """)
        
        with col2:
            st.info(f"""
            **Key Symptoms Matched:**
            {len(diagnosis['symptoms_matched'])} symptoms identified
            """)
        
        st.subheader("📊 Disease Risk Analysis")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            diseases = ['PCOS', 'Thyroid', 'Diabetes']
            risks = [
                predictions.get('pcos_risk', 0) * 100,
                predictions.get('thyroid_risk', 0) * 100,
                predictions.get('diabetes_risk', 0) * 100
            ]
            
            fig = go.Figure(data=[
                go.Bar(name='Risk Level', x=diseases, y=risks, 
                      marker_color=['#e91e63', '#ff9800', '#f44336'],
                      text=[f'{risk:.1f}%' for risk in risks],
                      textposition='auto')
            ])
            fig.update_layout(
                title='Disease Risk Assessment',
                yaxis_title='Risk Percentage (%)',
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Risk Levels:**")
            for disease, risk in zip(diseases, risks):
                risk_level = "High" if risk > 60 else "Medium" if risk > 30 else "Low"
                color = "🔴" if risk > 60 else "🟡" if risk > 30 else "🟢"
                st.write(f"{color} **{disease}:** {risk:.1f}% ({risk_level})")
        
        self.show_recommendations(predictions, diagnosis)

    def show_recommendations(self, predictions, diagnosis):
        st.markdown('<div class="sub-header">💡 Personalized Recommendations</div>', unsafe_allow_html=True)
        
        specialists = self.get_recommended_specialists(predictions)
        
        if specialists:
            st.subheader("👩‍⚕️ Recommended Specialists")
            
            for specialist in specialists:
                priority_text = "High Priority" if specialist['priority'] == 1 else "Medium Priority"
                color = "#e91e63" if specialist['priority'] == 1 else "#ff9800"
                
                st.markdown(f"""
                <div style='background-color: {color}20; padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin: 10px 0;'>
                    <h4 style='color: {color}; margin: 0 0 5px 0;'>{specialist['specialty']} - {priority_text}</h4>
                    <p style='color: #555; margin: 0;'>{specialist['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        doctors = db.get_doctors_by_specialty()
        if doctors:
            st.subheader("🏥 Available Doctors")
            
            for doctor in doctors[:5]:
                rating = doctor['rating']
                rating_color = "#4caf50" if rating >= 4.5 else "#ff9800" if rating >= 4.0 else "#f44336"
                
                st.markdown(f"""
                <div class="doctor-card">
                    <h4>👩‍⚕️ {doctor['name']}</h4>
                    <p><strong>Specialty:</strong> {doctor['specialty']}</p>
                    <p><strong>Hospital:</strong> {doctor['hospital']}, {doctor['location']}</p>
                    <p><strong>Rating:</strong> <span style='color: {rating_color}; font-weight: bold;'>{rating}/5 ⭐</span></p>
                    <p><strong>Contact:</strong> {doctor['contact']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.subheader("🎯 Specific Recommendations")
        if diagnosis['recommendations']:
            for rec in diagnosis['recommendations']:
                st.write(f"• {rec}")

    def calculate_overall_risk(self, predictions):
        max_risk = max(
            predictions.get('pcos_risk', 0),
            predictions.get('thyroid_risk', 0),
            predictions.get('diabetes_risk', 0)
        )
        
        if max_risk > 0.7:
            return "High"
        elif max_risk > 0.4:
            return "Medium"
        else:
            return "Low"

    def get_recommended_specialists(self, predictions):
        pcos_risk = predictions.get('pcos_risk', 0)
        thyroid_risk = predictions.get('thyroid_risk', 0)
        diabetes_risk = predictions.get('diabetes_risk', 0)
        
        specialists = []
        
        if pcos_risk >= 0.4:
            priority = 1 if pcos_risk >= 0.7 else 2
            specialists.append({
                'specialty': 'Gynecologist',
                'priority': priority,
                'reason': f'PCOS risk: {pcos_risk*100:.1f}%'
            })
        
        if thyroid_risk >= 0.4:
            priority = 1 if thyroid_risk >= 0.7 else 2
            specialists.append({
                'specialty': 'Endocrinologist',
                'priority': priority,
                'reason': f'Thyroid risk: {thyroid_risk*100:.1f}%'
            })
        
        if diabetes_risk >= 0.4:
            priority = 1 if diabetes_risk >= 0.7 else 2
            specialists.append({
                'specialty': 'Diabetologist',
                'priority': priority,
                'reason': f'Diabetes risk: {diabetes_risk*100:.1f}%'
            })
        
        if not specialists:
            specialists.append({
                'specialty': 'General Physician',
                'priority': 3,
                'reason': 'All risk levels are low. General check-up recommended.'
            })
        
        specialists.sort(key=lambda x: x['priority'])
        return specialists

if __name__ == "__main__":
    app = MedwiseApp()
    app.run()