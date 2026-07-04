variable "aws_region" {
  description = "AWS region for the Terraform bootstrap resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name portion of the naming convention."
  type        = string
  default     = "ai-debug-assistant"
}

variable "app_name" {
  description = "Short application name portion of the naming convention."
  type        = string
  default     = "ada"
}

variable "environment" {
  description = "Environment portion of the naming convention."
  type        = string
  default     = "bootstrap"
}

variable "state_bucket_suffix" {
  description = "Resource suffix used for the Terraform state bucket name."
  type        = string
  default     = "tf-state"
}

variable "lock_table_suffix" {
  description = "Resource suffix used for the Terraform lock table name."
  type        = string
  default     = "tf-lock"
}

variable "tags" {
  description = "Common tags applied to bootstrap resources."
  type        = map(string)
  default = {
    Project     = "ai-debug-assistant"
    App         = "ada"
    Environment = "bootstrap"
    ManagedBy   = "terraform"
  }
}
