variable "environment" {
  description = "Target deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS Cloud region for healthcare infrastructure"
  type        = string
  default     = "ap-south-1" # Hyderabad / Mumbai
}

variable "project_name" {
  description = "Project identifier tag"
  type        = string
  default     = "healthcare-dataops-pipeline"
}

variable "enable_hipaa_encryption" {
  description = "Enforce KMS Server-Side Encryption for all health storage tiers"
  type        = bool
  default     = true
}

variable "raw_data_retention_days" {
  description = "Number of days to retain raw audit records in bronze zone"
  type        = number
  default     = 90
}
