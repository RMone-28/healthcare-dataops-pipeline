import pytest
from src.data_generator import generate_synthetic_ehr_records
from src.deidentification import deidentify_ehr_dataframe, get_phi_audit_report


def test_hipaa_safe_harbor_masks_phi():
    raw_df = generate_synthetic_ehr_records(num_patients=5)
    deid_df = deidentify_ehr_dataframe(raw_df)

    # Names must be redacted
    assert (deid_df["first_name"] == "REDACTED").all()
    assert (deid_df["last_name"] == "REDACTED").all()

    # SSNs must be masked
    assert (deid_df["ssn"].str.startswith("***")).all()

    # Address must not be present in deid_df
    assert "address" not in deid_df.columns

    # Audit check
    audit = get_phi_audit_report(raw_df, deid_df)
    assert audit["hipaa_safe_harbor_compliant"] is True
    assert audit["unmasked_names_detected"] == 0
    assert audit["unmasked_ssn_detected"] == 0
