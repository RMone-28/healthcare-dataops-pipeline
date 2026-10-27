import pytest
from src.data_generator import generate_synthetic_ehr_records
from src.deidentification import deidentify_ehr_dataframe
from src.fhir_transformer import convert_dataframe_to_fhir_bundles


def test_fhir_transformation_structure():
    raw_df = generate_synthetic_ehr_records(num_patients=3)
    deid_df = deidentify_ehr_dataframe(raw_df)
    bundles = convert_dataframe_to_fhir_bundles(deid_df)

    assert len(bundles) == 3
    for b in bundles:
        assert b["resourceType"] == "Bundle"
        assert b["type"] == "collection"
        assert len(b["entry"]) >= 4  # Patient, Encounter, Condition, Observations

        # Check Patient resource
        patient_entry = b["entry"][0]["resource"]
        assert patient_entry["resourceType"] == "Patient"
        assert "id" in patient_entry
        assert patient_entry["gender"] in ["male", "female"]
