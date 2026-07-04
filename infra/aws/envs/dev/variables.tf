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

variable "enable_nat_gateway" {
  description = "Whether dev should create a NAT Gateway for private subnet outbound internet access."
  type        = bool
  default     = false
}

variable "enable_eks" {
  description = "Whether to create the short-lived dev EKS lab resources."
  type        = bool
  default     = false
}

variable "enable_rds" {
  description = "Future toggle for managed PostgreSQL labs. Default dev must not create RDS."
  type        = bool
  default     = false
}

variable "enable_elasticache" {
  description = "Future toggle for managed Redis or Valkey labs. Default dev must not create ElastiCache."
  type        = bool
  default     = false
}

variable "enable_alb" {
  description = "Future toggle for public AWS Load Balancer labs. Default dev must not create an ALB."
  type        = bool
  default     = false
}

variable "enable_container_insights" {
  description = "Future toggle for CloudWatch Container Insights. Default dev must not enable it."
  type        = bool
  default     = false
}

variable "eks_subnet_tier" {
  description = "Subnet tier used by the dev EKS lab: public for lower-cost labs or private for production-shaped networking."
  type        = string
  default     = "public"

  validation {
    condition     = contains(["public", "private"], var.eks_subnet_tier)
    error_message = "eks_subnet_tier must be either public or private."
  }
}

variable "cluster_version" {
  description = "Kubernetes version for the dev EKS cluster."
  type        = string
  default     = "1.35"
}

variable "node_desired_size" {
  description = "Desired number of worker nodes in dev."
  type        = number
  default     = 1
}

variable "node_min_size" {
  description = "Minimum number of worker nodes in dev."
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes in dev."
  type        = number
  default     = 1
}

variable "cluster_suffix" {
  description = "Suffix used to build the dev EKS cluster name."
  type        = string
  default     = "eks"
}

variable "authentication_mode" {
  description = "Authentication mode for the dev EKS cluster."
  type        = string
  default     = "API"
}

variable "node_group_suffix" {
  description = "Suffix used to build the dev managed node group name."
  type        = string
  default     = "general"
}

variable "node_instance_types" {
  description = "EC2 instance types used by the dev managed node group."
  type        = list(string)
  default     = ["t3.micro"]
}
