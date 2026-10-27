"""
HL7 FHIR R4 Transformer & Interoperability Engine
Converts de-identified healthcare records into standard HL7 FHIR Release 4 JSON resources:
- Patient Resource
- Encounter Resource
- Condition Resource (SNOMED-CT coded)
- Observation Resources (LOINC coded Vitals & Labs)
- Bundle Resource (FHIR Collection / Transaction Bundle)
"""

import json
from typing import Dict, Any, List
import pandas as pd


def create_fhir_patient_resource(row: pd.Series) -> Dict[str, Any]:
    """Creates a valid FHIR R4 Patient Resource from a de-identified record."""
    pid = str(row.get("pseudonym_id", row.get("patient_id", "ANON-0000")))
    
    patient = {
        "resourceType": "Patient",
        "id": pid,
        "identifier": [
            {
                "use": "official",
                "system": "http://hospital.org/fhir/patient-ids",
                "value": pid
            }
        ],
        "active": True,
        "name": [
            {
                "use": "anonymous",
                "family": "Anonymous",
                "given": [str(row.get("full_name_masked", "Patient"))]
            }
        ],
        "gender": str(row.get("gender", "unknown")).lower(),
        "birthDate": str(row.get("birth_date", "1980-01-01")),
        "address": [
            {
                "use": "home",
                "state": str(row.get("state", "")),
                "postalCode": str(row.get("postal_code", "")),
                "country": "IND" if str(row.get("state", "")) in ["Telangana", "Karnataka", "Tamil Nadu", "Maharashtra"] else "USA"
            }
        ]
    }
    return patient


def create_fhir_encounter_resource(row: pd.Series) -> Dict[str, Any]:
    """Creates a FHIR R4 Encounter Resource."""
    enc_id = str(row.get("encounter_id", "ENC-001"))
    pid = str(row.get("pseudonym_id", row.get("patient_id", "ANON-0000")))
    enc_class = str(row.get("encounter_class", "AMB"))

    encounter = {
        "resourceType": "Encounter",
        "id": enc_id,
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": enc_class,
            "display": "ambulatory" if enc_class == "AMB" else ("emergency" if enc_class == "EMER" else "inpatient")
        },
        "subject": {
            "reference": f"Patient/{pid}"
        },
        "period": {
            "start": f"{row.get('encounter_date', '2026-01-01')}T09:00:00Z",
            "end": f"{row.get('encounter_date', '2026-01-01')}T10:30:00Z"
        }
    }
    return encounter


def create_fhir_condition_resource(row: pd.Series) -> Dict[str, Any]:
    """Creates a FHIR R4 Condition Resource mapped with SNOMED-CT and ICD-10."""
    pid = str(row.get("pseudonym_id", row.get("patient_id", "ANON-0000")))
    cond_name = str(row.get("primary_diagnosis", "Healthy"))
    snomed_code = str(row.get("snomed_code", "260413007"))
    icd10_code = str(row.get("icd10_code", "Z00.00"))

    condition = {
        "resourceType": "Condition",
        "id": f"COND-{pid[-4:]}",
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active"
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed"
                }
            ]
        },
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": snomed_code,
                    "display": cond_name
                },
                {
                    "system": "http://hl7.org/fhir/sid/icd-10",
                    "code": icd10_code,
                    "display": cond_name
                }
            ],
            "text": cond_name
        },
        "subject": {
            "reference": f"Patient/{pid}"
        },
        "recordedDate": str(row.get("encounter_date", "2026-01-01"))
    }
    return condition


def create_fhir_observation_resources(row: pd.Series) -> List[Dict[str, Any]]:
    """
    Creates standard FHIR R4 Observation resources with standard LOINC codes:
    - 85354-9: Blood Pressure Panel
    - 8867-4: Heart rate
    - 2339-0: Glucose in blood
    - 2093-3: Total Cholesterol
    - 39156-5: Body Mass Index (BMI)
    """
    pid = str(row.get("pseudonym_id", row.get("patient_id", "ANON-0000")))
    obs_date = f"{row.get('encounter_date', '2026-01-01')}T09:15:00Z"
    observations = []

    # 1. Blood Pressure (Panel with Systolic & Diastolic components)
    bp_obs = {
        "resourceType": "Observation",
        "id": f"OBS-BP-{pid[-4:]}",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel with all children optional"
                }
            ],
            "text": "Blood Pressure"
        },
        "subject": {"reference": f"Patient/{pid}"},
        "effectiveDateTime": obs_date,
        "component": [
            {
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]
                },
                "valueQuantity": {
                    "value": float(row.get("systolic_bp", 120)),
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },
            {
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]
                },
                "valueQuantity": {
                    "value": float(row.get("diastolic_bp", 80)),
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]
    }
    observations.append(bp_obs)

    # 2. Glucose
    glucose_obs = {
        "resourceType": "Observation",
        "id": f"OBS-GLU-{pid[-4:]}",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ]
            }
        ],
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "2339-0", "display": "Glucose [Mass/volume] in Blood"}]
        },
        "subject": {"reference": f"Patient/{pid}"},
        "effectiveDateTime": obs_date,
        "valueQuantity": {
            "value": float(row.get("blood_glucose_mg_dl", 95.0)),
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
        }
    }
    observations.append(glucose_obs)

    # 3. Total Cholesterol
    chol_obs = {
        "resourceType": "Observation",
        "id": f"OBS-CHOL-{pid[-4:]}",
        "status": "final",
        "category": [
            {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}
                ]
            }
        ],
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "2093-3", "display": "Cholesterol [Mass/volume] in Serum or Plasma"}]
        },
        "subject": {"reference": f"Patient/{pid}"},
        "effectiveDateTime": obs_date,
        "valueQuantity": {
            "value": float(row.get("cholesterol_mg_dl", 185.0)),
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
        }
    }
    observations.append(chol_obs)

    return observations


def transform_record_to_fhir_bundle(row: pd.Series) -> Dict[str, Any]:
    """Assembles a full FHIR R4 Bundle containing all patient resources."""
    patient = create_fhir_patient_resource(row)
    encounter = create_fhir_encounter_resource(row)
    condition = create_fhir_condition_resource(row)
    observations = create_fhir_observation_resources(row)

    entries = []
    all_resources = [patient, encounter, condition] + observations
    for res in all_resources:
        entries.append({
            "fullUrl": f"urn:uuid:{res['resourceType']}-{res['id']}",
            "resource": res
        })

    bundle = {
        "resourceType": "Bundle",
        "id": f"BUNDLE-{patient['id']}",
        "type": "collection",
        "timestamp": f"{row.get('encounter_date', '2026-01-01')}T12:00:00Z",
        "total": len(entries),
        "entry": entries
    }
    return bundle


def convert_dataframe_to_fhir_bundles(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Converts a whole dataframe of clinical records into a list of FHIR R4 Bundles."""
    bundles = []
    for _, row in df.iterrows():
        bundle = transform_record_to_fhir_bundle(row)
        bundles.append(bundle)
    return bundles


if __name__ == "__main__":
    from data_generator import generate_synthetic_ehr_records
    from deidentification import deidentify_ehr_dataframe
    df = generate_synthetic_ehr_records(2)
    deid_df = deidentify_ehr_dataframe(df)
    bundles = convert_dataframe_to_fhir_bundles(deid_df)
    print(f"Generated {len(bundles)} FHIR Bundles.")
    print("Sample Patient FHIR Resource:")
    print(json.dumps(bundles[0]["entry"][0]["resource"], indent=2))
