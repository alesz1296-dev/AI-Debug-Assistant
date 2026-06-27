variable "aws_region" {
  description = "AWS region for the dev environment."
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
  description = "Environment name for this root module."
  type        = string
  default     = "dev"

  validation {
    condition     = var.environment == "dev"
    error_message = "The dev root module must use environment = \"dev\"."
  }
}

variable "tags" {
  description = "Additional tags merged into the standard dev environment tags."
  type        = map(string)
  default     = {}
}

variable "vpc_cidr" {
  description = "CIDR block for the dev VPC."
  type        = string
}

variable "availability_zones" {
  description = "Exactly two availability zones for the dev network."
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "availability_zones must contain exactly 2 values for dev."
  }
}

variable "public_subnet_cidrs" {
  description = "Exactly two CIDR blocks for the public subnets in dev."
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "public_subnet_cidrs must contain exactly 2 values for dev."
  }
}

variable "private_subnet_cidrs" {
  description = "Exactly two CIDR blocks for the private subnets in dev."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) == 2
    error_message = "private_subnet_cidrs must contain exactly 2 values for dev."
  }
}
