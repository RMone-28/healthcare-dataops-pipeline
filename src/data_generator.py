"""
Synthea-Style Synthetic Healthcare Data Generator
Generates realistic Electronic Health Records (EHR) containing:
- Demographics (Patient)
- Encounters (Visits)
- Observations (Vitals & Labs with LOINC codes)
- Conditions (Diagnoses with SNOMED-CT codes)
"""

import random
import uuid
from datetime import datetime, timedelta
import pandas as pd


FIRST_NAMES_M = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Suresh", "Ramesh", "Rahul", "Arjun", "Aditya"]
FIRST_NAMES_F = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Pooja", "Priya", "Ananya", "Lakshmi", "Sneha"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Sharma", "Reddy", "Patel", "Verma", "Rao", "Kumar", "Iyer"]
CITIES = [
    ("Hyderabad", "Telangana", "500001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Chennai", "Tamil Nadu", "600001"),
    ("Mumbai", "Maharashtra", "400001"),
    ("New York", "NY", "10001"),
    ("Chicago", "IL", "60601"),
    ("Austin", "TX", "73301")
]

CONDITIONS_CATALOG = [
    {"name": "Essential hypertension", "snomed": "59621000", "icd10": "I10"},
    {"name": "Type 2 diabetes mellitus", "snomed": "44054006", "icd10": "E11.9"},
    {"name": "Hyperlipidemia", "snomed": "55822004", "icd10": "E78.5"},
    {"name": "Asthma", "snomed": "195967001", "icd10": "J45.909"},
    {"name": "Normal / Healthy", "snomed": "260413007", "icd10": "Z00.00"}
]


def generate_synthetic_ehr_records(num_patients: int = 25, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic tabular EHR dataset simulating raw hospital intake records.
    """
    random.seed(seed)
    records = []
    base_date = datetime.now() - timedelta(days=365)

    for i in range(1, num_patients + 1):
        patient_id = f"PAT-{1000 + i}"
        gender = random.choice(["male", "female"])
        first_name = random.choice(FIRST_NAMES_M if gender == "male" else FIRST_NAMES_F)
        last_name = random.choice(LAST_NAMES)
        
        # Age between 18 and 80
        age = random.randint(18, 80)
        birth_year = datetime.now().year - age
        birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        # PII fields (to be protected by HIPAA Safe Harbor)
        ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        phone = f"+91-{random.randint(700, 999)}-{random.randint(1000000, 9999999)}"
        city_info = random.choice(CITIES)
        address = f"{random.randint(10, 999)} Healthway St, {city_info[0]}"
        
        # Clinical condition
        condition = random.choice(CONDITIONS_CATALOG)
        
        # Vitals and observations
        if condition["name"] == "Essential hypertension":
            systolic_bp = random.randint(140, 180)
            diastolic_bp = random.randint(90, 110)
        else:
            systolic_bp = random.randint(110, 130)
            diastolic_bp = random.randint(70, 85)

        if condition["name"] == "Type 2 diabetes mellitus":
            glucose = round(random.uniform(140.0, 240.0), 1)
        else:
            glucose = round(random.uniform(75.0, 115.0), 1)

        cholesterol = round(random.uniform(150.0, 260.0), 1)
        heart_rate = random.randint(60, 100)
        bmi = round(random.uniform(19.0, 34.0), 1)

        # Encounter data
        encounter_id = f"ENC-{uuid.uuid4().hex[:8].upper()}"
        encounter_days_ago = random.randint(1, 180)
        encounter_date = (datetime.now() - timedelta(days=encounter_days_ago)).strftime("%Y-%m-%d")
        encounter_class = random.choice(["AMB", "EMER", "IMP"])  # Ambulatory, Emergency, Inpatient

        record = {
            "patient_id": patient_id,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "birth_date": birth_date,
            "age": age,
            "ssn": ssn,
            "phone": phone,
            "address": address,
            "city": city_info[0],
            "state": city_info[1],
            "postal_code": city_info[2],
            "encounter_id": encounter_id,
            "encounter_date": encounter_date,
            "encounter_class": encounter_class,
            "primary_diagnosis": condition["name"],
            "snomed_code": condition["snomed"],
            "icd10_code": condition["icd10"],
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "blood_glucose_mg_dl": glucose,
            "cholesterol_mg_dl": cholesterol,
            "heart_rate_bpm": heart_rate,
            "bmi": bmi,
            "ingestion_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    sample_df = generate_synthetic_ehr_records(5)
    print(f"Generated {len(sample_df)} sample EHR records.")
    print(sample_df[["patient_id", "first_name", "last_name", "primary_diagnosis", "systolic_bp"]].head())
