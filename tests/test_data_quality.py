import pytest
from src.data_generator import generate_synthetic_ehr_records
from src.deidentification import deidentify_ehr_dataframe
from src.fhir_transformer import convert_dataframe_to_fhir_bundles
from src.data_quality import run_full_dataops_quality_suite


def test_dataops_quality_gate_passes_for_valid_data():
    raw_df = generate_synthetic_ehr_records(num_patients=5)
    deid_df = deidentify_ehr_dataframe(raw_df)
    bundles = convert_dataframe_to_fhir_bundles(deid_df)

    report = run_full_dataops_quality_suite(raw_df, deid_df, bundles)
    assert report["overall_status"] == "SUCCESS"
    assert report["failed_tests"] == 0
    assert report["pass_rate_percent"] == 100.0
