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

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "availability_zones" {
  description = "Availability zones used by the network module."
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "availability_zones must contain exactly 2 values for the current dev network design."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets."
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "public_subnet_cidrs must contain exactly 2 CIDR blocks for the current dev network design."
  }

  validation {
    condition     = length(var.public_subnet_cidrs) == length(var.availability_zones)
    error_message = "public_subnet_cidrs must match the number of availability_zones."
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) == 2
    error_message = "private_subnet_cidrs must contain exactly 2 CIDR blocks for the current dev network design."
  }

  validation {
    condition     = length(var.private_subnet_cidrs) == length(var.availability_zones)
    error_message = "private_subnet_cidrs must match the number of availability_zones."
  }
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway, NAT EIP, and private default outbound route."
  type        = bool
  default     = false
}
