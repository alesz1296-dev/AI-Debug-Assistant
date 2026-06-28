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

variable "node_group_suffix" {
  description = "Resource suffix appended to the standard naming prefix to build the managed node group name."
  type        = string
  validation {
    condition     = length(trim(var.node_group_suffix, " ")) > 0
    error_message = "node_group_suffix must not be empty."
  }
}

variable "node_instance_types" {
  description = "EC2 instance types used by the managed node group."
  type        = list(string)

  validation {
    condition     = length(var.node_instance_types) > 0
    error_message = "node_instance_types must contain at least one instance type."
  }
}

variable "node_desired_size" {
  description = "Desired number of nodes in the managed node group."
  type        = number

  validation {
    condition     = var.node_desired_size >= 0
    error_message = "node_desired_size must be greater than or equal to 0."
  }
}

variable "node_min_size" {
  description = "Minimum number of nodes in the managed node group."
  type        = number
  validation {
    condition     = var.node_min_size >= 0
    error_message = "node_min_size must be greater than or equal to 0."
  }
}

variable "node_max_size" {
  description = "Maximum number of nodes in the managed node group."
  type        = number

  validation {
    condition     = var.node_max_size >= 0
    error_message = "node_max_size must be greater than or equal to 0."
  }
}

variable "tags" {
  description = "Common tags applied to all EKS resources."
  type        = map(string)
  default     = {}
}

variable "cluster_suffix" {
  description = "Resource suffix appended to the standard naming prefix to build the EKS cluster name."
  type        = string

  validation {
    condition     = length(trim(var.cluster_suffix, " ")) > 0
    error_message = "cluster_suffix must not be empty."
  }
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS control plane."
  type        = string

  validation {
    condition     = can(regex("^1\\.[0-9]+$", var.cluster_version))
    error_message = "cluster_version must use the format 1.xx, for example 1.35."
  }
}

variable "subnet_ids" {
  description = "Subnet IDs used by the EKS cluster and managed node group."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "subnet_ids must contain at least 2 subnet IDs for the EKS deployment."
  }
}

variable "authentication_mode" {
  description = "Authentication mode for EKS cluster access configuration."
  type        = string
  default     = "API"

  validation {
    condition     = contains(["API", "API_AND_CONFIG_MAP", "CONFIG_MAP"], var.authentication_mode)
    error_message = "authentication_mode must be API, API_AND_CONFIG_MAP, or CONFIG_MAP."
  }
}