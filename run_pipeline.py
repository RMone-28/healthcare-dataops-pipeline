"""
Healthcare DataOps CLI Execution Runner
Can be executed standalone or within CI/CD pipelines:
  python run_pipeline.py --mode=full --records=20
  python run_pipeline.py --mode=test-gate
"""

import sys
import argparse
from src.pipeline_orchestrator import HealthcareDataOpsPipeline
from src.terraform_manager import TerraformManager


def main():
    parser = argparse.ArgumentParser(description="Healthcare DataOps Pipeline Runner")
    parser.add_argument("--mode", choices=["full", "test-gate", "iac-only"], default="full", help="Execution mode")
    parser.add_argument("--records", type=int, default=15, help="Number of synthetic EHR patient records")
    parser.add_argument("--env", type=str, default="dev", choices=["dev", "staging", "prod"], help="Target infrastructure environment")
    args = parser.parse_args()

    print("=" * 70)
    print("   HEALTHCARE DATAOPS INTEROPERABILITY PIPELINE")
    print(f"   Project: 23ME1A54C7 | Guide: Dr. P. Sudhakar")
    print("=" * 70)

    if args.mode in ["full", "iac-only"]:
        print(f"\n[1/2] Checking Infrastructure-as-Code (Terraform) for [{args.env}]...")
        tf_mgr = TerraformManager()
        val = tf_mgr.run_validate()
        print(f"  -> Config Validation: {'PASSED' if val['valid'] else 'FAILED'}")
        
        plan = tf_mgr.run_plan(args.env)
        print(f"  -> Execution Plan: {plan['total_add']} cloud resources ready for provisioning.")
        
        apply_res = tf_mgr.run_apply(args.env)
        print(f"  -> State Provisioned: {apply_res['status']} ({apply_res['resources_provisioned']} resources active)")

    if args.mode in ["full", "test-gate"]:
        print(f"\n[2/2] Executing DataOps Interoperability Pipeline ({args.records} Patient Records)...")
        pipeline = HealthcareDataOpsPipeline()
        result = pipeline.execute_pipeline(num_records=args.records)

        print(f"  -> Run ID: {result['pipeline_run_id']}")
        print(f"  -> Ingestion: {result['records_ingested']} records (Bronze S3 Layer)")
        print(f"  -> HIPAA De-identification: {'PASSED' if result['hipaa_safe_harbor_compliant'] else 'FAILED'}")
        print(f"  -> HL7 FHIR Bundles: {result['fhir_bundles_created']} bundles ({result['total_fhir_resources']} standard resources)")
        print(f"  -> DataOps Quality Gate: {result['data_quality_pass_rate']}% pass rate ({result['status']})")
        print(f"  -> Execution Time: {result['duration_seconds']}s")

        if result["status"] != "SUCCESS":
            print("\n[ERROR] DataOps quality assertions failed! Halting pipeline deployment.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print(" [SUCCESS] All DataOps & Infrastructure stages completed successfully!")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
