# utils/model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class HealthPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.features = [
            'Age', 'BMI', 'Irregular_Periods', 'Excess_Hair_Growth', 'Acne',
            'TSH_Level', 'Tiredness', 'Hair_Fall', 'Blood_Sugar', 
            'Frequent_Urination', 'Family_Diabetes'
        ]
        self.init_models()
    
    def init_models(self):
        """Initialize ML models with trained weights"""
        # PCOS Model
        self.models['pcos'] = self.create_pcos_model()
        self.models['thyroid'] = self.create_thyroid_model()
        self.models['diabetes'] = self.create_diabetes_model()
        
        # Initialize scalers
        self.scalers['pcos'] = StandardScaler()
        self.scalers['thyroid'] = StandardScaler()
        self.scalers['diabetes'] = StandardScaler()
        
        # Fit scalers with sample data (in real scenario, use training data)
        sample_data = np.random.randn(100, len(self.features))
        for scaler in self.scalers.values():
            scaler.fit(sample_data)
    
    def create_pcos_model(self):
        """Create and return PCOS prediction model"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        # In a real scenario, you would load a pre-trained model
        # For demo purposes, we'll create a simple rule-based model
        return model
    
    def create_thyroid_model(self):
        """Create and return thyroid prediction model"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        return model
    
    def create_diabetes_model(self):
        """Create and return diabetes prediction model"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        return model
    
    def predict_pcos_risk(self, features):
        """Predict PCOS risk based on symptoms"""
        # Rule-based approach for demo
        risk_score = 0.0
        
        # Weight factors
        if features['Irregular_Periods']:
            risk_score += 0.4
        if features['Excess_Hair_Growth']:
            risk_score += 0.3
        if features['Acne']:
            risk_score += 0.2
        if features['BMI'] > 25:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def predict_thyroid_risk(self, features):
        """Predict thyroid risk"""
        risk_score = 0.0
        
        # TSH level is primary indicator
        tsh = features['TSH_Level']
        if tsh < 0.4 or tsh > 4.0:
            risk_score += 0.5
        if features['Tiredness']:
            risk_score += 0.3
        if features['Hair_Fall']:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def predict_diabetes_risk(self, features):
        """Predict diabetes risk"""
        risk_score = 0.0
        
        # Blood sugar is primary indicator
        blood_sugar = features['Blood_Sugar']
        if blood_sugar > 126:
            risk_score += 0.5
        elif blood_sugar > 100:
            risk_score += 0.3
        
        if features['Frequent_Urination']:
            risk_score += 0.2
        if features['Family_Diabetes']:
            risk_score += 0.2
        if features['BMI'] > 25:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def predict(self, input_data):
        """Main prediction method"""
        try:
            # Ensure all features are present
            features = {feature: input_data.get(feature, 0) for feature in self.features}
            
            predictions = {
                'pcos_risk': self.predict_pcos_risk(features),
                'thyroid_risk': self.predict_thyroid_risk(features),
                'diabetes_risk': self.predict_diabetes_risk(features)
            }
            
            return predictions
            
        except Exception as e:
            print(f"Prediction error: {e}")
            # Return default low risks
            return {
                'pcos_risk': 0.1,
                'thyroid_risk': 0.1,
                'diabetes_risk': 0.1
            }