# PROJECT SYNOPSIS & ACADEMIC PROPOSAL

## Project Title
**CI/CD Practices for Data Pipelines (DataOps) via Infrastructure-as-code Provisioning (Terraform) for Pipeline Environments, Applied to Healthcare Records Interoperability Pipelines**

* **Candidate Roll No:** 23ME1A54C7
* **Domain:** Data Engineering & Pipelines
* **Supervisor / Guide:** Dr. P. Sudhakar
* **Academic Year:** 2026

---

### 1. Abstract
In modern healthcare informatics, clinical data exists in fragmented silos and legacy structures, preventing timely patient care and analytics. Transforming this data into global interoperability standards like HL7 FHIR (Fast Healthcare Interoperability Resources) requires robust, fault-tolerant data pipelines. However, traditional data engineering suffers from manual deployments, environment inconsistency ("it works on my machine"), and lack of automated data quality controls.

This project introduces an end-to-end **DataOps platform** that bridges software engineering CI/CD practices with data engineering and cloud infrastructure automation. Using **HashiCorp Terraform**, multi-tiered Medallion data lakes (Bronze, Silver, Gold) and PostgreSQL clinical repositories are provisioned declaratively as Infrastructure-as-Code (IaC). Ingestion pipelines automatically de-identify protected health information (PHI) under **HIPAA Safe Harbor** regulations (45 CFR § 164.514(b)) and map clinical observations to **HL7 FHIR R4** standards coded with LOINC and SNOMED-CT. Automated **Data Quality Gates** (Data CI) validate data contracts and physiological constraints before promoting data to analytical consumers.

---

### 2. Problem Statement
1. **Interoperability Deficit:** Clinical records lack uniform formatting across hospitals, complicating diagnostic exchange.
2. **Configuration Drift in Cloud Pipelines:** Manual setup of cloud buckets, access policies, and relational databases results in non-reproducible environments and security flaws.
3. **Absence of Data Quality CI Gates:** Downstream BI systems and clinical algorithms often ingest corrupt or unmasked PHI due to absence of automated pre-flight testing.

---

### 3. Proposed Methodology & Objectives
* **Objective 1 (IaC Automation):** Write modular Terraform scripts to provision reproducible Dev, Staging, and Production environments (S3, RDS, IAM, SQS, CloudWatch).
* **Objective 2 (Healthcare Interoperability):** Synthesize realistic EHR data and build transformation engines mapping clinical encounters, vitals, and conditions to HL7 FHIR R4 JSON bundles.
* **Objective 3 (Privacy & Compliance):** Enforce HIPAA Safe Harbor de-identification algorithm with 0% direct PHI leakage.
* **Objective 4 (DataOps CI/CD):** Develop a GitHub Actions pipeline running code linting, unit testing (pytest), data quality assertions (bounds and nullity checks), and terraform plan validation.
* **Objective 5 (Interactive Dashboard):** Implement a Streamlit control center for live pipeline execution, FHIR inspection, anomaly injection, and cloud state monitoring.

---

### 4. Technical Specifications
* **Programming & Processing:** Python 3.12, Pandas, DuckDB
* **Data Standards:** HL7 FHIR Release 4, LOINC, SNOMED-CT, ICD-10
* **Infrastructure as Code (IaC):** HashiCorp Terraform 1.7+ (AWS Provider)
* **Testing & Quality:** Pytest, Great Expectations-style Data Quality Gates
* **CI/CD Platform:** GitHub Actions Workflows
* **User Interface:** Streamlit Interactive Control Center

---

### 5. Expected Outcomes & Deliverables
1. Working DataOps CI/CD pipeline code with unit test suite passing at 100%.
2. Complete Terraform infrastructure scripts with state management.
3. Interactive Streamlit dashboard enabling real-time pipeline execution, FHIR bundle downloads, and live anomaly testing.
4. Comprehensive Project Report and Viva Voce preparation manual.
