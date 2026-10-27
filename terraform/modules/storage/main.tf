# Storage Module: Healthcare Data Lake Tiers (Bronze, Silver FHIR, Gold Analytics)

variable "environment" { type = string }
variable "project_name" { type = string }
variable "enable_encryption" { type = bool }

# 1. Bronze Tier: Raw Ingestion Zone
resource "aws_s3_bucket" "bronze_raw" {
  bucket = "${var.project_name}-raw-${var.environment}"
  tags = {
    Name        = "Raw Landing Zone (Bronze)"
    Environment = var.environment
    Compliance  = "HIPAA-Restricted"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bronze_crypto" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.bronze_raw.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 2. Silver Tier: De-identified & HL7 FHIR R4 Standardized Zone
resource "aws_s3_bucket" "silver_fhir" {
  bucket = "${var.project_name}-fhir-silver-${var.environment}"
  tags = {
    Name        = "Standardized FHIR Zone (Silver)"
    Environment = var.environment
    Standard    = "HL7-FHIR-R4"
  }
}

# 3. Gold Tier: Curated Analytical Data Mart
resource "aws_s3_bucket" "gold_curated" {
  bucket = "${var.project_name}-analytics-gold-${var.environment}"
  tags = {
    Name        = "Clinical Analytics Mart (Gold)"
    Environment = var.environment
    Consumer    = "PopulationHealth-BI"
  }
}

output "bronze_bucket_name" {
  value = aws_s3_bucket.bronze_raw.bucket
}

output "silver_bucket_name" {
  value = aws_s3_bucket.silver_fhir.bucket
}

output "gold_bucket_name" {
  value = aws_s3_bucket.gold_curated.bucket
}
