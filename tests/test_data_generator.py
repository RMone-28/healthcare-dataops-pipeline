import pytest
from src.data_generator import generate_synthetic_ehr_records


def test_generate_synthetic_ehr_records_count():
    df = generate_synthetic_ehr_records(num_patients=10)
    assert len(df) == 10
    assert "patient_id" in df.columns
    assert "systolic_bp" in df.columns
    assert "diastolic_bp" in df.columns
    assert "primary_diagnosis" in df.columns


def test_vital_signs_within_clinical_expectations():
    df = generate_synthetic_ehr_records(num_patients=20, seed=123)
    assert (df["systolic_bp"] >= 90).all()
    assert (df["diastolic_bp"] >= 50).all()
    assert (df["heart_rate_bpm"] >= 50).all()
    assert (df["blood_glucose_mg_dl"] >= 60).all()
