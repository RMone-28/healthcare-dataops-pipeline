"""
End-to-End Healthcare DataOps Pipeline Orchestrator
Coordinates:
1. Ingestion: Raw synthetic patient EHR records (Bronze)
2. Security & Compliance: HIPAA Safe Harbor De-identification
3. Interoperability: HL7 FHIR R4 Standard Resource Transformation (Silver)
4. DataOps Gate: Automated Quality & Integrity Assertions
5. Load: FHIR repository and analytical marts (Gold)
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Tuple
import pandas as pd

from src.data_generator import generate_synthetic_ehr_records
from src.deidentification import deidentify_ehr_dataframe, get_phi_audit_report
from src.fhir_transformer import convert_dataframe_to_fhir_bundles
from src.data_quality import run_full_dataops_quality_suite


class HealthcareDataOpsPipeline:
    def __init__(self, base_data_dir: str = None):
        if base_data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_data_dir = os.path.join(project_root, "data")
        else:
            self.base_data_dir = base_data_dir

        self.raw_dir = os.path.join(self.base_data_dir, "raw")
        self.deid_dir = os.path.join(self.base_data_dir, "deidentified")
        self.fhir_dir = os.path.join(self.base_data_dir, "fhir_bundles")
        self.reports_dir = os.path.join(self.base_data_dir, "reports")

        for d in [self.raw_dir, self.deid_dir, self.fhir_dir, self.reports_dir]:
            os.makedirs(d, exist_ok=True)

    def execute_pipeline(self, num_records: int = 15, seed: int = 42) -> Dict[str, Any]:
        """Runs the complete DataOps pipeline from raw ingestion to FHIR loading."""
        start_time = datetime.utcnow()
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 1: Ingestion (Bronze Layer)
        raw_df = generate_synthetic_ehr_records(num_patients=num_records, seed=seed)
        raw_csv_path = os.path.join(self.raw_dir, f"raw_ehr_batch_{timestamp_str}.csv")
        raw_df.to_csv(raw_csv_path, index=False)

        # Step 2: HIPAA Safe Harbor De-identification
        deid_df = deidentify_ehr_dataframe(raw_df)
        deid_csv_path = os.path.join(self.deid_dir, f"deid_ehr_batch_{timestamp_str}.csv")
        deid_df.to_csv(deid_csv_path, index=False)
        phi_audit = get_phi_audit_report(raw_df, deid_df)

        # Step 3: HL7 FHIR R4 Transformation
        fhir_bundles = convert_dataframe_to_fhir_bundles(deid_df)
        fhir_json_path = os.path.join(self.fhir_dir, f"fhir_bundle_{timestamp_str}.json")
        with open(fhir_json_path, "w", encoding="utf-8") as f:
            json.dump(fhir_bundles, f, indent=2)

        # Step 4: DataOps Quality Gate Execution
        dq_report = run_full_dataops_quality_suite(raw_df, deid_df, fhir_bundles)
        report_path = os.path.join(self.reports_dir, f"dq_report_{timestamp_str}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(dq_report, f, indent=2)

        elapsed_sec = round((datetime.utcnow() - start_time).total_seconds(), 2)

        total_fhir_resources = sum(b.get("total", 0) for b in fhir_bundles)

        return {
            "pipeline_run_id": f"RUN-{timestamp_str}",
            "status": "SUCCESS" if dq_report["overall_status"] == "SUCCESS" else "FAILED",
            "duration_seconds": elapsed_sec,
            "records_ingested": len(raw_df),
            "fhir_bundles_created": len(fhir_bundles),
            "total_fhir_resources": total_fhir_resources,
            "data_quality_pass_rate": dq_report["pass_rate_percent"],
            "hipaa_safe_harbor_compliant": phi_audit["hipaa_safe_harbor_compliant"],
            "artifacts": {
                "raw_file": raw_csv_path,
                "deidentified_file": deid_csv_path,
                "fhir_file": fhir_json_path,
                "report_file": report_path
            },
            "phi_audit": phi_audit,
            "quality_report": dq_report,
            "raw_dataframe": raw_df,
            "deid_dataframe": deid_df,
            "fhir_bundles": fhir_bundles
        }


if __name__ == "__main__":
    pipeline = HealthcareDataOpsPipeline()
    result = pipeline.execute_pipeline(num_records=5)
    print("Pipeline Execution Completed!")
    print(f"Status: {result['status']} | Duration: {result['duration_seconds']}s")
    print(f"Total FHIR Resources: {result['total_fhir_resources']}")
    print(f"Quality Pass Rate: {result['data_quality_pass_rate']}%")
