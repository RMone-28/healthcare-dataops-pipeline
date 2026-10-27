# Healthcare DataOps Infrastructure as Code (Terraform)
# Provisions S3 Data Lake (Bronze/Silver/Gold), RDS PostgreSQL Clinical DB,
# IAM Roles for DataOps Runners, and Pipeline Monitoring Alarms.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "RollNo-23ME1A54C7"
      Guide       = "Dr-P-Sudhakar"
    }
  }
}

# 1. Medallion Storage Module (Bronze, Silver FHIR, Gold Analytics)
module "storage" {
  source            = "./modules/storage"
  project_name      = var.project_name
  environment       = var.environment
  enable_encryption = var.enable_hipaa_encryption
}

# 2. Interoperability Database Module
module "database" {
  source       = "./modules/database"
  project_name = var.project_name
  environment  = var.environment
}

# 3. IAM Execution Role for DataOps Pipeline CI/CD Runner
resource "aws_iam_role" "dataops_pipeline_runner" {
  name = "${var.project_name}-runner-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Role = "DataOps-Automated-Execution"
  }
}

# 4. SQS Queue for Ingestion Trigger
resource "aws_sqs_queue" "ehr_ingest_queue" {
  name                      = "${var.project_name}-ingest-events-${var.environment}"
  message_retention_seconds = 86400 # 1 day
}

# 5. CloudWatch Metric Alarm for Pipeline Failure Alert
resource "aws_cloudwatch_metric_alarm" "pipeline_error_alarm" {
  alarm_name          = "${var.project_name}-failure-alarm-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "PipelineFailures"
  namespace           = "Healthcare/DataOps"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers when healthcare interoperability pipeline encounters schema or validation errors"
}
