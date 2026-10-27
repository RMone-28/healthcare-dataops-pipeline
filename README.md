# CI/CD Practices for Data Pipelines (DataOps) via Infrastructure-as-Code Provisioning (Terraform) for Pipeline Environments, Applied to Healthcare Records Interoperability Pipelines

**Student ID / Roll No:** `23ME1A54C7`  
**Guide / Supervisor:** `Dr. P. Sudhakar`  
**Domain:** `Data Engineering & Pipelines`  

---

## 📌 Executive Summary
This project demonstrates an enterprise-grade **DataOps platform** implementing automated Continuous Integration and Continuous Deployment (CI/CD) practices for healthcare records interoperability pipelines. 

By integrating **HashiCorp Terraform** for Infrastructure-as-Code (IaC), the system automates cloud resource provisioning across Medallion data lake tiers (Bronze, Silver, Gold). Clinical electronic health records (EHR) are anonymized following **HIPAA Safe Harbor** guidelines (45 CFR § 164.514(b)) and transformed into standardized **HL7 FHIR Release 4 (R4)** JSON bundles with LOINC and SNOMED-CT codings. Automated **Data Quality Gates** (Data CI) validate biological validity, schema completeness, and privacy compliance prior to promotion.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────┐
│     Raw EHR Intake (Bronze)     │  Synthetic Patient Records with Vitals & Lab Results
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   HIPAA De-identification Gate  │  Direct PHI Redacted, Cryptographic Tokenization
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    HL7 FHIR R4 Transformer      │  Patient, Encounter, Condition (SNOMED), Observation (LOINC)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   DataOps Quality Assertions    │  Great Expectations-style gates (Bounds, Nulls, Schemas)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Terraform Cloud Provisioning  │  S3 Medallion Tiers, RDS Postgres DB, IAM Roles, Alarms
└─────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Launch the Interactive Web Dashboard
Run the one-click launcher on Windows:
```cmd
run_app.bat
```
Or execute via terminal:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 2. Run the CLI DataOps Pipeline
```bash
python run_pipeline.py --mode=full --records=20 --env=dev
```

### 3. Run the Automated Test Suite
```bash
pytest -v
```

---

## 📁 Repository Structure
```
healthcare-dataops-pipeline/
├── .github/
│   └── workflows/
│       └── dataops_ci_cd.yml       # GitHub Actions 4-Stage CI/CD Workflow
├── terraform/                      # Infrastructure as Code (IaC)
│   ├── main.tf                     # Root Terraform AWS provider & modules
│   ├── variables.tf                # Environment & cloud variables
│   ├── outputs.tf                  # S3 bucket ARNs, DB endpoints
│   ├── terraform.tfvars            # Dev configuration values
│   └── modules/
│       ├── storage/main.tf         # S3 Medallion Data Lake (Bronze/Silver/Gold)
│       └── database/main.tf        # FHIR Interoperability PostgreSQL DB
├── src/                            # Pipeline Source Code
│   ├── data_generator.py           # Synthea-style EHR generator
│   ├── deidentification.py         # HIPAA Safe Harbor anonymization
│   ├── fhir_transformer.py         # HL7 FHIR R4 resource mapper
│   ├── data_quality.py             # DataOps quality gate suite
│   ├── pipeline_orchestrator.py    # Pipeline coordinator & execution engine
│   └── terraform_manager.py        # Terraform HCL validator & state manager
├── tests/                          # Automated Pytest Suite
│   ├── test_data_generator.py
│   ├── test_deidentification.py
│   ├── test_fhir_transformer.py
│   └── test_data_quality.py
├── data/                           # Generated Data Lake Tiers
│   ├── raw/                        # Ingested CSV EHR records
│   ├── deidentified/               # Anonymized records
│   ├── fhir_bundles/               # HL7 FHIR R4 JSON bundles
│   └── reports/                    # Quality validation reports
├── app.py                          # Streamlit UI Control Center
├── run_pipeline.py                 # Standalone CLI runner
├── run_app.bat                     # Windows 1-click batch launcher
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation
```

---

## 🛡️ Standards & Compliance
1. **HIPAA Safe Harbor (45 CFR § 164.514(b)(2)):** All 18 direct identifiers (names, SSNs, phone numbers, exact addresses) are redacted or tokenized.
2. **HL7 FHIR Release 4:** Fully compliant JSON resources for interoperability across electronic health systems.
3. **Medical Terminologies:** LOINC (vitals & laboratory measurements) and SNOMED-CT (clinical diagnoses).
4. **DataOps CI/CD:** Shift-left testing, automated data contracts, and IaC pipeline environments.
