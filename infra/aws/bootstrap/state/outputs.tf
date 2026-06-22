
output "state_bucket_name" {
  description = "Name of the S3 bucket used for Terraform state."
  value       = local.state_bucket_name
}

output "lock_table_name" {
  description = "Name of the DynamoDB table used for Terraform locking."
  value       = local.lock_table_name
}

output "aws_region" {
  description = "AWS region where bootstrap resources were created."
  value       = var.aws_region
}

output "name_prefix" {
  description = "Shared naming prefix for bootstrap resources."
  value       = local.name_prefix
}
