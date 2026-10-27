"""
DataOps Quality Gates & Validation Engine (Great Expectations Style)
Implements automated CI data quality assertions for healthcare pipelines:
- Schema completeness
- Nullity and presence checks
- Range & Boundary assertions for vital signs
- FHIR R4 Structural & Referential Integrity
- Privacy Compliance Check
"""

from typing import Dict, Any, List
import pandas as pd


class DataQualityGate:
    def __init__(self):
        self.results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def assert_rule(self, name: str, category: str, passed: bool, details: str = ""):
        """Records an assertion result."""
        status = "PASSED" if passed else "FAILED"
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        self.results.append({
            "test_name": name,
            "category": category,
            "status": status,
            "passed": passed,
            "details": details
        })

    def validate_raw_schema(self, df: pd.DataFrame) -> bool:
        """Validates that all mandatory hospital EHR fields are present."""
        required_cols = [
            "patient_id", "first_name", "last_name", "gender", "birth_date",
            "systolic_bp", "diastolic_bp", "blood_glucose_mg_dl", "primary_diagnosis"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        self.assert_rule(
            name="Raw Schema Completeness",
            category="Schema",
            passed=len(missing) == 0,
            details=f"Missing columns: {missing}" if missing else "All required EHR columns present"
        )
        return len(missing) == 0

    def validate_vital_ranges(self, df: pd.DataFrame) -> bool:
        """Validates that vital signs fall within biologically valid physiological bounds."""
        # 1. Systolic BP
        bad_sbp = df[(df["systolic_bp"] < 60) | (df["systolic_bp"] > 260)]
        self.assert_rule(
            name="Systolic BP Physiological Bound [60-260 mmHg]",
            category="Data Consistency",
            passed=len(bad_sbp) == 0,
            details=f"{len(bad_sbp)} outliers detected" if len(bad_sbp) > 0 else "All values within valid clinical range"
        )

        # 2. Diastolic BP
        bad_dbp = df[(df["diastolic_bp"] < 40) | (df["diastolic_bp"] > 160)]
        self.assert_rule(
            name="Diastolic BP Physiological Bound [40-160 mmHg]",
            category="Data Consistency",
            passed=len(bad_dbp) == 0,
            details=f"{len(bad_dbp)} outliers detected" if len(bad_dbp) > 0 else "All values within valid clinical range"
        )

        # 3. Blood Glucose
        bad_glucose = df[(df["blood_glucose_mg_dl"] < 40) | (df["blood_glucose_mg_dl"] > 500)]
        self.assert_rule(
            name="Blood Glucose Physiological Bound [40-500 mg/dL]",
            category="Data Consistency",
            passed=len(bad_glucose) == 0,
            details=f"{len(bad_glucose)} outliers detected" if len(bad_glucose) > 0 else "All values within valid bounds"
        )
        return len(bad_sbp) == 0 and len(bad_dbp) == 0 and len(bad_glucose) == 0

    def validate_privacy_compliance(self, deid_df: pd.DataFrame) -> bool:
        """Validates that no plain text names or unmasked SSNs exist in the dataset."""
        unmasked_ssn = deid_df[~deid_df["ssn"].str.startswith("***", na=False)]
        unmasked_names = deid_df[deid_df["first_name"] != "REDACTED"]

        self.assert_rule(
            name="HIPAA Safe Harbor SSN Redaction Gate",
            category="Security & Privacy",
            passed=len(unmasked_ssn) == 0,
            details=f"Unmasked SSNs detected: {len(unmasked_ssn)}" if len(unmasked_ssn) > 0 else "Zero unmasked SSNs found"
        )

        self.assert_rule(
            name="HIPAA Safe Harbor Name Redaction Gate",
            category="Security & Privacy",
            passed=len(unmasked_names) == 0,
            details=f"Unmasked names detected: {len(unmasked_names)}" if len(unmasked_names) > 0 else "All direct names redacted"
        )
        return len(unmasked_ssn) == 0 and len(unmasked_names) == 0

    def validate_fhir_bundles(self, bundles: List[Dict[str, Any]]) -> bool:
        """Validates structural compliance with the HL7 FHIR R4 standard."""
        all_valid = True
        invalid_types = 0
        missing_subjects = 0

        for b in bundles:
            if b.get("resourceType") != "Bundle" or "entry" not in b:
                all_valid = False
                continue

            for entry in b.get("entry", []):
                res = entry.get("resource", {})
                rtype = res.get("resourceType")
                if rtype not in ["Patient", "Encounter", "Condition", "Observation"]:
                    invalid_types += 1
                if rtype in ["Observation", "Condition", "Encounter"]:
                    if "subject" not in res or not res["subject"].get("reference", "").startswith("Patient/"):
                        missing_subjects += 1

        self.assert_rule(
            name="HL7 FHIR R4 Resource Type Compliance",
            category="Interoperability",
            passed=invalid_types == 0,
            details=f"{invalid_types} unexpected resource types" if invalid_types > 0 else "All resources adhere to standard FHIR R4 types"
        )

        self.assert_rule(
            name="FHIR Patient Referential Integrity Gate",
            category="Interoperability",
            passed=missing_subjects == 0,
            details=f"{missing_subjects} broken references" if missing_subjects > 0 else "All clinical resources correctly reference Patient ID"
        )

        return all_valid and invalid_types == 0 and missing_subjects == 0

    def get_summary(self) -> Dict[str, Any]:
        """Returns the complete DataOps quality report."""
        total = self.passed_tests + self.failed_tests
        pass_rate = round((self.passed_tests / total * 100), 1) if total > 0 else 0.0
        return {
            "total_tests": total,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "pass_rate_percent": pass_rate,
            "overall_status": "SUCCESS" if self.failed_tests == 0 else "FAILED_GATES",
            "results": self.results
        }


def run_full_dataops_quality_suite(raw_df: pd.DataFrame, deid_df: pd.DataFrame, fhir_bundles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Runs the complete end-to-end DataOps quality gate suite."""
    gate = DataQualityGate()
    gate.validate_raw_schema(raw_df)
    gate.validate_vital_ranges(raw_df)
    gate.validate_privacy_compliance(deid_df)
    gate.validate_fhir_bundles(fhir_bundles)
    return gate.get_summary()


if __name__ == "__main__":
    from data_generator import generate_synthetic_ehr_records
    from deidentification import deidentify_ehr_dataframe
    from fhir_transformer import convert_dataframe_to_fhir_bundles

    raw = generate_synthetic_ehr_records(5)
    deid = deidentify_ehr_dataframe(raw)
    bundles = convert_dataframe_to_fhir_bundles(deid)
    report = run_full_dataops_quality_suite(raw, deid, bundles)
    print("Quality Pass Rate:", report["pass_rate_percent"], "%")
    print("Status:", report["overall_status"])
