variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
  default     = "ai-debug-assistant"
}

variable "app_name" {
  description = "Short application name used in resource naming."
  type        = string
  default     = "ada"
}

variable "environment" {
  description = "Environment name, such as dev, staging, or prod."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "tags" {
  description = "Common tags applied to all network resources."
  type        = map(string)
  default     = {}
}


variable "repository_suffix" {
  description = "Resource suffix appended to the standard naming prefix to build the ECR repository name."
  type        = string
}

variable "image_tag_mutability" {
  description = "Whether image tags in the repository can be overwritten after being pushed, such as MUTABLE or IMMUTABLE."
  type        = string

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "image_tag_mutability must be either MUTABLE or IMMUTABLE."
  }
}

variable "scan_on_push" {
  description = "Whether Amazon ECR should automatically scan pushed container images for known vulnerabilities."
  type        = bool
}

variable "lifecycle_keep_count" {
  description = "Number of recent container images to retain before older images are expired by the repository lifecycle policy."
  type        = number

  validation {
    condition     = var.lifecycle_keep_count > 0
    error_message = "lifecycle_keep_count must be greater than 0."
  }
}
