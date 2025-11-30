import sqlite3
import hashlib
import pandas as pd
import numpy as np

class UserDatabase:
    def __init__(self, db_path="feminine.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create assessment history table with correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                bmi REAL,
                tsh_level REAL,
                blood_sugar REAL,
                irregular_periods INTEGER,
                excess_hair_growth INTEGER,
                acne INTEGER,
                tiredness INTEGER,
                hair_fall INTEGER,
                frequent_urination INTEGER,
                family_pcos INTEGER,
                family_thyroid INTEGER,
                family_diabetes INTEGER,
                pcos_risk REAL,
                thyroid_risk REAL,
                diabetes_risk REAL,
                overall_risk TEXT,
                primary_disease TEXT,
                confidence REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        # Create doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                hospital TEXT NOT NULL,
                location TEXT NOT NULL,
                rating REAL,
                contact TEXT
            )
        ''')
        
        # Insert demo users if they don't exist
        demo_users = [
            ("demo", "demo123", "demo@example.com"),
            ("test", "test123", "test@example.com"),
            ("admin", "admin123", "admin@example.com")
        ]
        
        for username, password, email in demo_users:
            if not self.user_exists(username):
                self.create_user(username, password, email)
        
        # Insert comprehensive doctors data
        self.insert_comprehensive_doctors()
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash = result[0]
            input_hash = self.hash_password(password)
            return stored_hash == input_hash
        
        return False
    
    def user_exists(self, username):
        """Check if user exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def save_assessment(self, username, assessment_data):
        """Save assessment to database"""
        try:
            input_data = assessment_data['input_data']
            predictions = assessment_data['predictions']
            diagnosis = assessment_data.get('disease_diagnosis', {})
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO assessment_history (
                    username, name, age, bmi, tsh_level, blood_sugar,
                    irregular_periods, excess_hair_growth, acne, tiredness, hair_fall,
                    frequent_urination, family_pcos, family_thyroid, family_diabetes,
                    pcos_risk, thyroid_risk, diabetes_risk, overall_risk, primary_disease, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username,
                assessment_data['name'],
                input_data['Age'],
                input_data['BMI'],
                input_data['TSH_Level'],
                input_data['Blood_Sugar'],
                input_data['Irregular_Periods'],
                input_data['Excess_Hair_Growth'],
                input_data['Acne'],
                input_data['Tiredness'],
                input_data['Hair_Fall'],
                input_data['Frequent_Urination'],
                0,  # family_pcos
                0,  # family_thyroid
                input_data['Family_Diabetes'],
                predictions['pcos_risk'],
                predictions['thyroid_risk'],
                predictions['diabetes_risk'],
                assessment_data['overall_risk'],
                diagnosis.get('primary_disease', 'Unknown'),
                diagnosis.get('confidence', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving assessment: {e}")
            return False
    
    def get_user_assessments(self, username):
        """Get all assessments for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM assessment_history 
                WHERE username = ? 
                ORDER BY timestamp DESC
            ''', (username,))
            
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            conn.close()
            
            assessments = []
            for row in results:
                assessment = dict(zip(columns, row))
                # Convert to the format expected by the app
                assessment['input_data'] = {
                    'Age': assessment['age'],
                    'BMI': assessment['bmi'],
                    'TSH_Level': assessment['tsh_level'],
                    'Blood_Sugar': assessment['blood_sugar'],
                    'Irregular_Periods': assessment['irregular_periods'],
                    'Excess_Hair_Growth': assessment['excess_hair_growth'],
                    'Acne': assessment['acne'],
                    'Tiredness': assessment['tiredness'],
                    'Hair_Fall': assessment['hair_fall'],
                    'Frequent_Urination': assessment['frequent_urination'],
                    'Family_Diabetes': assessment['family_diabetes']
                }
                assessment['predictions'] = {
                    'pcos_risk': assessment['pcos_risk'],
                    'thyroid_risk': assessment['thyroid_risk'],
                    'diabetes_risk': assessment['diabetes_risk']
                }
                assessment['disease_diagnosis'] = {
                    'primary_disease': assessment['primary_disease'],
                    'confidence': assessment['confidence']
                }
                assessments.append(assessment)
            
            return assessments
        except Exception as e:
            print(f"Error getting assessments: {e}")
            return []
    
    def insert_comprehensive_doctors(self):
        """Insert comprehensive doctors data with all locations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if doctors already exist
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Comprehensive list of doctors with diverse locations
            doctors_data = [
                # General Physicians - Various locations
                ("Dr. Jagadeeshwari", "General Physician", "Meenakshi Hospitals", "Madurai", 4.5, "+91-9876543201"),
                ("Dr. Nazneen", "General Physician", "Deepan Hospitals", "Coimbatore", 4.3, "+91-9876543202"),
                ("Dr. Regina Kumari", "General Physician", "Medcare Center", "Chennai", 4.6, "+91-9876543203"),
                ("Dr. Sophia Priya", "General Physician", "Silverline Hospitals", "Sivagangai", 4.4, "+91-9876543204"),
                ("Dr. Nivetha", "General Physician", "Sunrise Health", "Tanjore", 4.2, "+91-9876543205"),
                ("Dr. Sunil Prasath", "General Physician", "Menagha Clinic", "Tiruchirappalli", 4.1, "+91-9876543206"),
                ("Dr. Rohan Mehra", "General Physician", "Artemis Hospital", "Gurgaon", 4.3, "+91-9876543227"),
                ("Dr. Pooja Desai", "General Physician", "Sir Ganga Ram Hospital", "Delhi", 4.5, "+91-9876543228"),
                
                # Gynecologists - Various locations
                ("Dr. Meera Rao", "Gynecologist", "City Women Care", "Karaikudi", 4.8, "+91-9876543207"),
                ("Dr. Sahana Gupta", "Gynecologist", "Elite Wellness", "Chennai", 4.7, "+91-9876543208"),
                ("Dr. Kavita Sharma", "Gynecologist", "City Women Care", "Kancheepuram", 4.9, "+91-9876543209"),
                ("Dr. Priya Sharma", "Gynecologist", "Apollo Hospital", "Delhi", 4.8, "+91-9876543210"),
                ("Dr. Anjali Mehta", "Gynecologist", "Fortis Hospital", "Mumbai", 4.7, "+91-9876543211"),
                ("Dr. Radhika Iyer", "Gynecologist", "Kokilaben Hospital", "Mumbai", 4.8, "+91-9876543212"),
                ("Dr. Sunita Reddy", "Gynecologist", "Max Hospital", "Chennai", 4.6, "+91-9876543243"),
                ("Dr. Meera Rao", "Gynecologist", "City Women Care", "Bengaluru", 4.7, "+91-9876543244"),
                
                # Endocrinologists - Various locations
                ("Dr. Sandhya Jain", "Endocrinologist", "Sunrise Health", "Vellore", 4.7, "+91-9876543213"),
                ("Dr. Anjali Menon", "Endocrinologist", "Trust Clinic", "Hyderabad", 4.6, "+91-9876543214"),
                ("Dr. Rajesh Kumar", "Endocrinologist", "Apollo Hospital", "Delhi", 4.7, "+91-9876543215"),
                ("Dr. Meera Patel", "Endocrinologist", "Columbia Asia", "Pune", 4.5, "+91-9876543216"),
                ("Dr. Neha Gupta", "Endocrinologist", "Medanta Hospital", "Gurgaon", 4.8, "+91-9876543217"),
                ("Dr. Ananya Das", "Endocrinologist", "Narayana Health", "Kolkata", 4.7, "+91-9876543236"),
                ("Dr. Sanjay Verma", "Endocrinologist", "Fortis Hospital", "Bangalore", 4.6, "+91-9876543237"),
                ("Dr. Sunitha", "Endocrinologist", "Sunrise Health", "Theni", 4.6, "+91-9876543217"),
                ("Dr. Angel Kannan", "Endocrinologist", "Trust Clinic", "Kochi", 4.5, "+91-9876543218"),
                
                # Diabetologists - Various locations
                ("Dr. Priya Nair", "Diabetologist", "Silverline Hospitals", "Delhi", 4.8, "+91-9876543218"),
                ("Dr. Lata Verma", "Diabetologist", "Sunrise Health", "Mumbai", 4.7, "+91-9876543219"),
                ("Dr. Arun Malhotra", "Diabetologist", "Max Hospital", "Delhi", 4.7, "+91-9876543229"),
                ("Dr. Preeti Joshi", "Diabetologist", "Ruby Hall Clinic", "Pune", 4.6, "+91-9876543230"),
                ("Dr. Vikram Singh", "Diabetologist", "Apollo Hospital", "Chennai", 4.8, "+91-9876543231"),
                ("Dr. Sameer Khan", "Diabetologist", "Lilavati Hospital", "Mumbai", 4.9, "+91-9876543233"),
                ("Dr. Nandini Rao", "Diabetologist", "KIMS Hospital", "Hyderabad", 4.5, "+91-9876543232"),
                ("Dr. Princy Mary", "Diabetologist", "Silverline Hospitals", "Tiruchirappalli", 4.6, "+91-9876543221"),
                ("Dr. Preethi Shreine", "Diabetologist", "Sunrise Health", "Kochi", 4.5, "+91-9876543222"),
            ]
            
            cursor.executemany(
                "INSERT INTO doctors (name, specialty, hospital, location, rating, contact) VALUES (?, ?, ?, ?, ?, ?)",
                doctors_data
            )
        
        conn.commit()
        conn.close()
    
    def get_doctors_by_specialty(self, specialty=None, location=None):
        """Get doctors filtered by specialty and location"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM doctors WHERE 1=1"
        params = []
        
        if specialty and specialty != 'All':
            query += " AND specialty = ?"
            params.append(specialty)
        
        if location and location != 'All':
            query += " AND location = ?"
            params.append(location)
        
        query += " ORDER BY rating DESC"
        
        cursor.execute(query, params)
        doctors = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = ['id', 'name', 'specialty', 'hospital', 'location', 'rating', 'contact']
        return [dict(zip(columns, doctor)) for doctor in doctors]
    
    def get_all_specialties(self):
        """Get all unique specialties"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty")
        specialties = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return specialties
    
    def get_all_locations(self):
        """Get all unique locations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT location FROM doctors ORDER BY location")
        locations = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return locations

# Global database instance
db = UserDatabase()