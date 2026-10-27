output "environment" {
  description = "Target deployment tier"
  value       = var.environment
}

output "bronze_raw_bucket" {
  description = "Raw Landing Zone S3 Bucket"
  value       = module.storage.bronze_bucket_name
}

output "silver_fhir_bucket" {
  description = "Standardized FHIR R4 S3 Bucket"
  value       = module.storage.silver_bucket_name
}

output "gold_analytics_bucket" {
  description = "Curated Analytics S3 Bucket"
  value       = module.storage.gold_bucket_name
}

output "database_endpoint" {
  description = "FHIR Clinical RDS Database Endpoint"
  value       = module.database.db_endpoint
}

output "pipeline_runner_iam_role" {
  description = "IAM Role ARN for CI/CD Runner"
  value       = aws_iam_role.dataops_pipeline_runner.arn
}

output "ingest_queue_url" {
  description = "SQS Queue for Real-Time Hospital EHR Ingestion"
  value       = aws_sqs_queue.ehr_ingest_queue.id
}
