# Database Module: Interoperability Clinical Store (PostgreSQL)

variable "environment" { type = string }
variable "project_name" { type = string }

resource "aws_db_instance" "fhir_clinical_db" {
  identifier          = "${var.project_name}-db-${var.environment}"
  allocated_storage   = 20
  engine              = "postgres"
  engine_version      = "15.4"
  instance_class      = var.environment == "prod" ? "db.t4g.large" : "db.t4g.micro"
  db_name             = "fhir_interop_${var.environment}"
  username            = "dataops_admin"
  password            = "HealthOps2026Secure!"
  skip_final_snapshot = true
  publicly_accessible = false

  tags = {
    Name        = "FHIR Interoperability DB"
    Environment = var.environment
    ManagedBy   = "Terraform-DataOps"
  }
}

output "db_endpoint" {
  value = aws_db_instance.fhir_clinical_db.endpoint
}

output "db_name" {
  value = aws_db_instance.fhir_clinical_db.db_name
}
