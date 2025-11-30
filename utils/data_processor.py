import pandas as pd
import numpy as np
from database import db

class DataProcessor:
    def __init__(self):
        self.doctors_data = self.load_doctors_data()
    
    def load_doctors_data(self):
        """Load doctors data from database"""
        return db.get_doctors_by_specialty()
    
    def get_recommended_doctors(self, predictions, max_doctors=5):
        """Get recommended doctors based on risk predictions"""
        # Determine which specialties to recommend
        specialties = []
        
        pcos_risk = predictions.get('pcos_risk', 0)
        thyroid_risk = predictions.get('thyroid_risk', 0)
        diabetes_risk = predictions.get('diabetes_risk', 0)
        
        if pcos_risk >= 0.4:
            specialties.append('Gynecologist')
        if thyroid_risk >= 0.4:
            specialties.append('Endocrinologist')
        if diabetes_risk >= 0.4:
            specialties.append('Diabetologist')
        
        # If no specific risks, recommend general physician
        if not specialties:
            specialties.append('General Physician')
        
        # Get doctors for recommended specialties
        recommended_doctors = []
        for specialty in specialties:
            specialty_doctors = [doc for doc in self.doctors_data if doc['specialty'] == specialty]
            recommended_doctors.extend(specialty_doctors)
        
        # Sort by rating and return top doctors
        recommended_doctors.sort(key=lambda x: x['rating'], reverse=True)
        return recommended_doctors[:max_doctors]
    
    def get_doctors_data(self, specialty=None, location=None):
        """Get doctors data filtered by specialty and location"""
        return db.get_doctors_by_specialty(specialty, location)
    
    def get_all_specialties(self):
        """Get all available specialties"""
        return db.get_all_specialties()
    
    def get_all_locations(self):
        """Get all available locations"""
        return db.get_all_locations()
    
    def process_health_data(self, input_data):
        """Process health data for analysis"""
        processed_data = input_data.copy()
        
        # Normalize numerical values
        if 'BMI' in processed_data:
            processed_data['BMI Category'] = self.categorize_bmi(processed_data['BMI'])
        
        if 'TSH_Level' in processed_data:
            processed_data['TSH Category'] = self.categorize_tsh(processed_data['TSH_Level'])
        
        if 'Blood_Sugar' in processed_data:
            processed_data['Sugar Category'] = self.categorize_blood_sugar(processed_data['Blood_Sugar'])
        
        return processed_data
    
    def categorize_bmi(self, bmi):
        """Categorize BMI values"""
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def categorize_tsh(self, tsh):
        """Categorize TSH values"""
        if tsh < 0.4:
            return 'Low (Hyperthyroidism)'
        elif tsh <= 4.0:
            return 'Normal'
        else:
            return 'High (Hypothyroidism)'
    
    def categorize_blood_sugar(self, sugar):
        """Categorize blood sugar values"""
        if sugar < 70:
            return 'Low'
        elif sugar <= 100:
            return 'Normal'
        elif sugar <= 125:
            return 'Pre-diabetes'
        else:
            return 'Diabetes'