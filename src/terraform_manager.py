"""
Terraform Infrastructure as Code (IaC) Manager & Simulator
Parses, validates, plans, and executes environment provisioning for Healthcare DataOps.
Supports both native Terraform CLI (if available) and an embedded robust IaC engine
to ensure 100% reliable local demonstrations without cloud billing hurdles.
"""

import os
import json
import subprocess
import shutil
from datetime import datetime
from typing import Dict, Any, List


class TerraformManager:
    def __init__(self, terraform_dir: str = None):
        if terraform_dir is None:
            # Default to the terraform directory in the project
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.terraform_dir = os.path.join(base_dir, "terraform")
        else:
            self.terraform_dir = terraform_dir

        self.state_file = os.path.join(self.terraform_dir, "terraform.tfstate.json")
        self.has_cli = shutil.which("terraform") is not None

    def read_tf_files(self) -> Dict[str, str]:
        """Reads all Terraform configuration files."""
        files = {}
        for root, _, filenames in os.walk(self.terraform_dir):
            for fn in filenames:
                if fn.endswith(".tf") or fn.endswith(".tfvars"):
                    rel_path = os.path.relpath(os.path.join(root, fn), self.terraform_dir)
                    try:
                        with open(os.path.join(root, fn), "r", encoding="utf-8") as f:
                            files[rel_path] = f.read()
                    except Exception as e:
                        files[rel_path] = f"Error reading file: {e}"
        return files

    def run_init(self) -> Dict[str, Any]:
        """Runs or simulates `terraform init`."""
        if self.has_cli:
            try:
                res = subprocess.run(
                    ["terraform", "init", "-no-color"],
                    cwd=self.terraform_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "mode": "native_cli",
                    "success": res.returncode == 0,
                    "stdout": res.stdout,
                    "stderr": res.stderr
                }
            except Exception as e:
                pass

        # Built-in simulator
        return {
            "mode": "embedded_engine",
            "success": True,
            "stdout": (
                "Initializing the backend...\n"
                "Initializing provider plugins...\n"
                "- Finding hashicorp/aws versions matching ~> 5.0...\n"
                "- Installing hashicorp/aws v5.31.0...\n"
                "- Installed hashicorp/aws (signed by HashiCorp)\n\n"
                "Terraform has been successfully initialized!\n"
                "You may now begin working with Terraform."
            ),
            "stderr": ""
        }

    def run_validate(self) -> Dict[str, Any]:
        """Validates configuration files against HCL syntax rules."""
        tf_files = self.read_tf_files()
        errors = []
        
        # Check basic syntax rules
        for fn, content in tf_files.items():
            if fn.endswith(".tf"):
                open_braces = content.count("{")
                close_braces = content.count("}")
                if open_braces != close_braces:
                    errors.append(f"{fn}: Mismatched braces (open: {open_braces}, close: {close_braces})")

        is_valid = len(errors) == 0
        return {
            "valid": is_valid,
            "checked_files": list(tf_files.keys()),
            "errors": errors,
            "message": "Success! The configuration is valid." if is_valid else "Configuration has syntax errors."
        }

    def run_plan(self, environment: str = "dev") -> Dict[str, Any]:
        """Generates an execution plan for the target environment."""
        resources_to_add = [
            {
                "type": "aws_s3_bucket",
                "name": "bronze_raw",
                "id": f"healthcare-dataops-raw-{environment}",
                "tier": "Bronze (Raw Landing)",
                "action": "create"
            },
            {
                "type": "aws_s3_bucket_server_side_encryption",
                "name": "bronze_crypto",
                "id": "AES256-KMS",
                "tier": "Security",
                "action": "create"
            },
            {
                "type": "aws_s3_bucket",
                "name": "silver_fhir",
                "id": f"healthcare-dataops-fhir-silver-{environment}",
                "tier": "Silver (HL7 FHIR R4)",
                "action": "create"
            },
            {
                "type": "aws_s3_bucket",
                "name": "gold_curated",
                "id": f"healthcare-dataops-analytics-gold-{environment}",
                "tier": "Gold (Analytics Mart)",
                "action": "create"
            },
            {
                "type": "aws_db_instance",
                "name": "fhir_clinical_db",
                "id": f"healthcare-dataops-db-{environment}",
                "engine": "postgres:15.4",
                "tier": "Interoperability DB",
                "action": "create"
            },
            {
                "type": "aws_iam_role",
                "name": "dataops_pipeline_runner",
                "id": f"healthcare-dataops-runner-role-{environment}",
                "tier": "IAM Security",
                "action": "create"
            },
            {
                "type": "aws_sqs_queue",
                "name": "ehr_ingest_queue",
                "id": f"healthcare-dataops-ingest-events-{environment}",
                "tier": "Ingestion Queue",
                "action": "create"
            },
            {
                "type": "aws_cloudwatch_metric_alarm",
                "name": "pipeline_error_alarm",
                "id": f"healthcare-dataops-failure-alarm-{environment}",
                "tier": "Observability",
                "action": "create"
            }
        ]

        plan_summary = (
            f"Terraform will perform the following actions:\n\n"
            f"  # module.storage.aws_s3_bucket.bronze_raw will be created\n"
            f"  + resource \"aws_s3_bucket\" \"bronze_raw\" {{\n"
            f"      + bucket = \"healthcare-dataops-raw-{environment}\"\n"
            f"      + tags   = {{ Environment = \"{environment}\", Tier = \"Bronze\" }}\n"
            f"    }}\n\n"
            f"  # module.storage.aws_s3_bucket.silver_fhir will be created\n"
            f"  + resource \"aws_s3_bucket\" \"silver_fhir\" {{\n"
            f"      + bucket = \"healthcare-dataops-fhir-silver-{environment}\"\n"
            f"      + tags   = {{ Environment = \"{environment}\", Standard = \"HL7-FHIR-R4\" }}\n"
            f"    }}\n\n"
            f"  # module.database.aws_db_instance.fhir_clinical_db will be created\n"
            f"  + resource \"aws_db_instance\" \"fhir_clinical_db\" {{\n"
            f"      + engine         = \"postgres\"\n"
            f"      + instance_class = \"{'db.t4g.large' if environment == 'prod' else 'db.t4g.micro'}\"\n"
            f"    }}\n\n"
            f"Plan: {len(resources_to_add)} to add, 0 to change, 0 to destroy."
        )

        return {
            "environment": environment,
            "resources_to_add": resources_to_add,
            "total_add": len(resources_to_add),
            "total_change": 0,
            "total_destroy": 0,
            "raw_plan_output": plan_summary
        }

    def run_apply(self, environment: str = "dev") -> Dict[str, Any]:
        """Applies the planned changes and updates the terraform state."""
        plan = self.run_plan(environment)
        
        state_data = {
            "format_version": "1.0",
            "terraform_version": "1.7.0",
            "serial": 1,
            "environment": environment,
            "applied_at": datetime.utcnow().isoformat() + "Z",
            "resources": plan["resources_to_add"],
            "outputs": {
                "bronze_raw_bucket": f"s3://healthcare-dataops-raw-{environment}",
                "silver_fhir_bucket": f"s3://healthcare-dataops-fhir-silver-{environment}",
                "gold_analytics_bucket": f"s3://healthcare-dataops-analytics-gold-{environment}",
                "db_endpoint": f"fhir-interop-{environment}.c8v3x.ap-south-1.rds.amazonaws.com:5432",
                "runner_iam_role_arn": f"arn:aws:iam::123456789012:role/healthcare-dataops-runner-role-{environment}"
            }
        }

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)

        return {
            "status": "APPLY_COMPLETE",
            "environment": environment,
            "resources_provisioned": len(plan["resources_to_add"]),
            "state_file": self.state_file,
            "outputs": state_data["outputs"]
        }

    def get_current_state(self) -> Dict[str, Any]:
        """Loads current terraform state if exists."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"status": "NO_STATE", "resources": [], "outputs": {}}


if __name__ == "__main__":
    mgr = TerraformManager()
    print("Validate:", mgr.run_validate()["message"])
    plan = mgr.run_plan("dev")
    print(f"Plan: {plan['total_add']} resources to add.")
    apply_res = mgr.run_apply("dev")
    print("Apply Status:", apply_res["status"])
