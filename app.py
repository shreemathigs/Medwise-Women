import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.model import HealthPredictor
from utils.data_processor import DataProcessor
from database import db
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="Medwise-Women",
    page_icon="heart",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    st.markdown("""
    <style>
    .main-header {font-size: 3rem; color: #e91e63; text-align: center; font-weight: bold;}
    .sub-header {font-size: 1.8rem; color: #ad1457; text-align: center; font-weight: bold;}
    .tagline {font-size: 1.2rem; color: #666; text-align: center; font-style: italic;}
    .risk-low {background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50; color: #2e7d32;}
    .risk-medium {background-color: #fff3e0; padding: 15px; border-radius: 10px; border-left: 5px solid #ff9800; color: #ef6c00;}
    .risk-high {background-color: #ffebee; padding: 15px; border-radius: 10px; border-left: 5px solid #f44336; color: #c62828;}
    .admin-header {font-size: 2.8rem; color: #e91e63; text-align: center; margin: 2rem 0;}
    .metric-card {background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;}
    .metric-value {font-size: 2.5rem; font-weight: bold; color: #e91e63;}
    .metric-label {color: #666; margin-top: 8px;}
    .doctor-card {background: #fce4ec; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0; border-left: 4px solid #e91e63;color: black}
    .bmi-calculator-card {background: #e3f2fd; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; margin: 15px 0; color: #0d47a1}
    .health-implications-card {background: #fff3e0; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #ff9800; color: #e65100;}
    </style>
    """, unsafe_allow_html=True)

class MedwiseApp:
    def __init__(self):
        self.initialize_session_state()
        self.predictor = HealthPredictor()
        self.processor = DataProcessor()
        load_css()

    def initialize_session_state(self):
        defaults = {
            'authenticated': False, 
            'current_user': None, 
            'assessment_history': [],
            'last_assessment': None, 
            'current_page': "Home", 
            'doctors': [],
            'form_data': {
                'name': '', 'age': 25, 'bmi': 22.0, 'tsh_level': 2.5, 'blood_sugar': 100,
                'irregular_periods': False, 'excess_hair_growth': False, 'acne': False,
                'tiredness': False, 'hair_fall': False, 'frequent_urination': False,
                'family_diabetes': False
            },
            'bmi_result': None, 
            'bmi_category': None,
            'login_error': None
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def login_page(self):
        st.markdown('<div class="main-header">Medwise-Women</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Patient Health & Hospital Recommendation System</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login", type="primary")
                
                if login_btn:
                    if username and password:
                        if db.authenticate_user(username, password):
                            st.session_state.authenticated = True
                            st.session_state.current_user = username
                            st.session_state.assessment_history = db.get_user_assessments(username)
                            db.log_login(username)
                            st.session_state.login_error = None
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.session_state.login_error = "Invalid credentials"
                            st.error("Invalid credentials")
                    else:
                        st.error("Please enter username and password")

        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email (optional)")
                signup_btn = st.form_submit_button("Sign Up")
                
                if signup_btn:
                    if new_user and new_pass:
                        if new_pass != confirm:
                            st.error("Passwords do not match")
                        elif db.create_user(new_user, new_pass, email):
                            st.success("Account created! You can now log in.")
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Please enter username and password")

        st.info("Demo: `demo` / `demo123` | `admin` / `admin123`")

    def sidebar(self):
        with st.sidebar:
            st.image("assets/medwiselogo.png", use_column_width=True, caption="Medwise-Women")

            menu = ["Home", "Reference Ranges", "Health Assessment", "BMI Calculator",
                     "Doctor Recommendations", "Health History", "Disease Information"]
            icons = ['house', 'book', 'activity', 'calculator', 'person-lines-fill', 'clock-history', 'info-circle']

            if st.session_state.current_user == "admin":
                menu.append("Admin Panel")
                icons.append("shield-lock")

            menu.append("Logout")
            icons.append("box-arrow-right")

            choice = option_menu("Menu", menu, icons=icons, menu_icon="heart-pulse", default_index=0)

            if choice == "Logout":
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            st.session_state.current_page = choice

    def admin_panel(self):
        st.markdown('<div class="admin-header">Admin Dashboard</div>', unsafe_allow_html=True)
        
        data = db.get_analytics()

        # 4 Big Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{data['total_users']}</div>
                <div class='metric-label'>Total Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{data['total_assessments']}</div>
                <div class='metric-label'>Total Assessments</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{data['total_logins']}</div>
                <div class='metric-label'>Total Logins</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{data['active_users']}</div>
                <div class='metric-label'>Active Users (30 days)</div>
             </div>
            """, unsafe_allow_html=True)


        # User Growth Chart
        st.subheader("User Growth Over Time")
        if data['users_growth']:
            df_growth = pd.DataFrame(data['users_growth'])
            if not df_growth.empty:
                df_growth['date'] = pd.to_datetime(df_growth['date'])
                # Sort by date to ensure correct order
                df_growth = df_growth.sort_values('date')

                fig = px.line(
                    df_growth,
                    x='date',
                    y='count',
                    title='User Growth Over Time',
                    markers=True,                  # shows small circles on line
                )

                # Customize layout
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Users",
                    hovermode="x unified",        
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No new users registered yet.")

       
        # Diagnosis Pie Chart
        st.subheader("Diagnosis Distribution")
        feminine_colors = ['#e91e63', '#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4']

        if data['assessment_distribution']:
            df_pie = pd.DataFrame(data['assessment_distribution'])
            if not df_pie.empty and 'disease' in df_pie.columns and 'count' in df_pie.columns:
                fig = px.pie(
                    df_pie,
                    values='count',
                    names='disease',
                    color_discrete_sequence=feminine_colors   
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No assessments recorded yet.")

        # Tabs: All Users & Recent Activity
        tab1, tab2 = st.tabs(["All Registered Users", "Recent Assessments"])

        with tab1:
            if data['all_users']:
                df_users = pd.DataFrame(data['all_users'])
                if not df_users.empty:
                    st.dataframe(df_users, use_container_width=True, hide_index=True)
                else:
                    st.write("No users found.")
            else:
                st.write("No users found.")

        with tab2:
            if data['recent_assessments']:
                df_assess = pd.DataFrame(data['recent_assessments'])
                if not df_assess.empty:
                    st.dataframe(df_assess, use_container_width=True, hide_index=True)
                else:
                    st.write("No recent assessments.")
            else:
                st.write("No recent assessments.")

    def run(self):
        if not st.session_state.authenticated:
            self.login_page()
            return

        self.sidebar()

        page = st.session_state.current_page
        if page == "Home": 
            self.home_page()
        elif page == "Reference Ranges": 
            self.reference_ranges_page()
        elif page == "Health Assessment": 
            self.assessment_page()
        elif page == "BMI Calculator": 
            self.bmi_calculator_page()
        elif page == "Doctor Recommendations": 
            self.doctor_recommendations_page()
        elif page == "Health History": 
            self.history_page()
        elif page == "Disease Information": 
            self.disease_info_page()
        elif page == "Admin Panel" and st.session_state.current_user == "admin":
            self.admin_panel()

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
            
            st.markdown("---")
            st.info("💡 **Get Started**: Use the sidebar navigation on the left to access Health Assessment and other features!")
        
        with col2:
            st.markdown("""
            <div style='background: #e8f5e9; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                <h4 style='color: #2e7d32; text-align: center;'>📈 Health Stats</h4>
                <p style='text-align: center; color: #555; margin: 0;'>
                    Regular health assessments can help in early detection and prevention of diseases.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: #e3f2fd; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                <h4 style='color: #1565c0; text-align: center;'>🏆 Why Choose Medwise?</h4>
                <p style='text-align: center; color: #555; margin: 0;'>
                    Personalized • Accurate • Secure • Women-Focused
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def reference_ranges_page(self):
        st.markdown('<div class="main-header">Reference Ranges</div>', unsafe_allow_html=True)
        st.markdown("### Normal Health Parameter Ranges for Women")

        # BMI Categories
        st.markdown("""
        <div style="background:#e8f5e9;padding:20px;border-radius:12px;border-left:6px solid #4caf50;margin:15px 0;">
            <h3 style="color:#2e7d32;margin:0;">📏 BMI Categories</h3>
            <ul style="color:#1b5e20;">
                <li><strong>Underweight:</strong> &lt; 18.5</li>
                <li><strong>Normal:</strong> 18.5 – 24.9</li>
                <li><strong>Overweight:</strong> 25 – 29.9</li>
                <li><strong>Obese:</strong> ≥ 30</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Blood Sugar
        st.markdown("""
        <div style="background:#fff3e0;padding:20px;border-radius:12px;border-left:6px solid #ff9800;margin:15px 0;">
            <h3 style="color:#ef6c00;margin:0;">🩸 Blood Sugar (mg/dL)</h3>
            <ul style="color:#e65100;">
                <li><strong>Normal:</strong> 70 – 99</li>
                <li><strong>Pre-diabetes:</strong> 100 – 125</li>
                <li><strong>Diabetes:</strong> ≥ 126</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # TSH Level
        st.markdown("""
        <div style="background:#e3f2fd;padding:20px;border-radius:12px;border-left:6px solid #2196f3;margin:15px 0;">
            <h3 style="color:#1565c0;margin:0;">🦋 TSH Level (mIU/L)</h3>
            <ul style="color:#0d47a1;">
                <li><strong>Normal:</strong> 0.4 – 4.0</li>
                <li><strong>Low:</strong> &lt; 0.4 → Hyperthyroidism</li>
                <li><strong>High:</strong> &gt; 4.0 → Hypothyroidism</li>
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
        
        with st.form("health_assessment", clear_on_submit=False):
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
                family_diabetes = st.checkbox("Family History of Diabetes", value=form_data['family_diabetes'])
            
            submitted = st.form_submit_button("Assess My Health", type="primary")
            
            if submitted:
                st.session_state.form_data = {
                    'name': name, 'age': age, 'bmi': bmi, 'tsh_level': tsh_level, 'blood_sugar': blood_sugar,
                    'irregular_periods': irregular_periods, 'excess_hair_growth': excess_hair_growth, 'acne': acne,
                    'tiredness': tiredness, 'hair_fall': hair_fall, 'frequent_urination': frequent_urination,
                    'family_diabetes': family_diabetes
                }
                
                self.process_assessment(name, age, bmi, tsh_level, blood_sugar, irregular_periods, 
                                      excess_hair_growth, acne, tiredness, hair_fall, frequent_urination, 
                                      family_diabetes)
        
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
                <h3 style="color:#0d47a1;margin:0">📊 BMI Calculator</h3>
                <p>Calculate your Body Mass Index (BMI) to understand your weight category and health risks.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if 'bmi_calc_done' not in st.session_state:
                st.session_state.bmi_calc_done = False
            
            with st.form("bmi_calculator"):
                st.subheader("Calculate Your BMI")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=165.0, step=0.1, key="height_cm")
                
                with col_b:
                    weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=60.0, step=0.1, key="weight_kg")
                
                calculate_bmi = st.form_submit_button("Calculate BMI", type="primary", use_container_width=True)
                
                if calculate_bmi:
                    height_m = height_cm / 100
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
                    
                    st.session_state.bmi_result = bmi
                    st.session_state.bmi_category = category
                    st.session_state.bmi_color = color
                    st.session_state.bmi_advice = advice
                    st.session_state.bmi_calc_done = True
            
            if st.session_state.bmi_calc_done and st.session_state.bmi_result is not None:
                bmi = st.session_state.bmi_result
                category = st.session_state.bmi_category
                color = st.session_state.bmi_color
                advice = st.session_state.bmi_advice
                
                st.markdown("---")
                st.success(f"**Your BMI Result: {bmi:.1f}**")
                st.markdown(f"""
                <div style='background-color: {color}20; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; margin: 15px 0;'>
                    <h4 style='color: {color}; margin: 0 0 10px 0;'>Category: {category}</h4>
                    <p style='color: #555; margin: 0;'>{advice}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # BMI Gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = bmi,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "BMI Score", 'font': {'size': 24}},
                    gauge = {
                        'axis': {'range': [None, 40], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': color, 'thickness': 0.8},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 18.5], 'color': "#e3f2fd"},
                            {'range': [18.5, 25], 'color': "#e8f5e9"},
                            {'range': [25, 30], 'color': "#fff3e0"},
                            {'range': [30, 40], 'color': "#ffebee"}
                        ],
                        'threshold': {
                            'line': {'color': color, 'width': 4},
                            'thickness': 0.75,
                            'value': bmi
                        }
                    }
                ))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                if st.button("Calculate New BMI", type="secondary"):
                    st.session_state.bmi_calc_done = False
                    st.session_state.bmi_result = None
                    st.session_state.bmi_category = None
                    st.rerun()
        
        with col2:
            st.markdown("""
            <div style="background:#e8f5e9;padding:20px;border-radius:12px;border-left:6px solid #4caf50;margin:15px 0;">
                <h3 style="color:#2e7d32;margin:0;">BMI Reference Chart</h3>
                <ul style="color:#1b5e20;">
                    <li><strong>&lt; 18.5</strong> → Underweight</li>
                    <li><strong>18.5 – 24.9</strong> → Normal</li>
                    <li><strong>25 – 29.9</strong> → Overweight</li>
                    <li><strong>≥ 30</strong> → Obese</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="health-implications-card">
                <h4 style="color:#e65100;margin:0;">🏥 Health Implications</h4>
                <p><strong>High BMI (≥25) may increase risk of:</strong></p>
                <ul>
                    <li>Heart disease</li>
                    <li>Type 2 Diabetes</li>
                    <li>High blood pressure</li>
                    <li>Stroke</li>
                    <li>Certain cancers</li>
                    <li>Sleep apnea</li>
                </ul>
                <p><strong>Low BMI (&lt;18.5) may indicate:</strong></p>
                <ul>
                    <li>Nutritional deficiencies</li>
                    <li>Weakened immune system</li>
                    <li>Osteoporosis risk</li>
                    <li>Anemia</li>
                    <li>Irregular periods</li>
                </ul>
                <p><em>Note: BMI is a screening tool. Consult a healthcare provider for personalized assessment.</em></p>
            </div>
            """, unsafe_allow_html=True)

    def doctor_recommendations_page(self):
        st.markdown('<div class="main-header">Find Specialists & Hospitals</div>', unsafe_allow_html=True)
        st.info("👨‍⚕️ Search for doctors by specialty and location. Our database includes specialists across India.")
        
        all_specialties = ['All'] + db.get_all_specialties()
        all_locations = ['All'] + db.get_all_locations()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            specialty = st.selectbox("Specialty", all_specialties, index=0)
        
        with col2:
            location = st.selectbox("Location", all_locations, index=0)
        
        with col3:
            st.write("")
            st.write("")
            search_btn = st.button("🔍 Search Doctors", type="primary", use_container_width=True)
        
        if search_btn:
            doctors_data = db.get_doctors_by_specialty(
                specialty if specialty != 'All' else None, 
                location if location != 'All' else None
            )
            st.session_state.doctors = doctors_data
            
            if doctors_data:
                st.success(f"✅ Found {len(doctors_data)} doctor(s) matching your criteria")
            else:
                st.warning("⚠️ No doctors found matching your criteria. Try adjusting your filters.")
        
        # Always show some doctors initially or after search
        doctors_to_display = st.session_state.doctors if st.session_state.doctors else db.get_doctors_by_specialty(None, None)
        
        if doctors_to_display:
            st.subheader(f"👨‍⚕️ Available Doctors ({len(doctors_to_display)})")
            
            for doctor in doctors_to_display[:20]:  # Limit to 20 for display
                rating = doctor['rating']
                rating_color = "#4caf50" if rating >= 4.5 else "#ff9800" if rating >= 4.0 else "#f44336"
                
                st.markdown(f"""
                <div class="doctor-card">
                    <h4 style="color: #e91e63; margin-bottom: 10px;">👨‍⚕️ {doctor['name']}</h4>
                    <p><strong>Specialty:</strong> {doctor['specialty']}</p>
                    <p><strong>Hospital:</strong> {doctor['hospital']}, {doctor['location']}</p>
                    <p><strong>Rating:</strong> <span style='color: {rating_color}; font-weight: bold;'>{rating}/5 ⭐</span></p>
                    <p><strong>Contact:</strong> {doctor['contact']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👆 Use the filters above to search for doctors")

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
                          hair_fall, frequent_urination, family_diabetes):
        
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
        
        # Set text color based on risk level
        if overall_risk == "High":
            text_color = "#c62828"  # Dark red for high risk
        elif overall_risk == "Medium":
            text_color = "#ef6c00"  # Dark orange for medium risk
        else:
            text_color = "#2e7d32"  # Dark green for low risk
    

        st.markdown(f"""
        <div class="{risk_class}">
            <h3 style = color:{text_color};margin:0;>Overall Health Risk: {overall_risk}</h3>
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
        
        # Show doctors from database
        doctors = db.get_doctors_by_specialty()
        if doctors:
            st.subheader("🏥 Available Doctors in Database")
            
            for doctor in doctors[:5]:
                rating = doctor['rating']
                rating_color = "#4caf50" if rating >= 4.5 else "#ff9800" if rating >= 4.0 else "#f44336"
                
                st.markdown(f"""
                <div class="doctor-card">
                    <h4 style="color: #e91e63; margin-bottom: 10px;">👩‍⚕️ {doctor['name']}</h4>
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