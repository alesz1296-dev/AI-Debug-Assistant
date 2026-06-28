aws_region = "us-east-1"

project_name = "ai-debug-assistant"
app_name     = "ada"
environment  = "dev"

#network VPC variables
vpc_cidr = "10.10.0.0/16"

availability_zones = [
  "us-east-1a",
  "us-east-1b",
]

public_subnet_cidrs = [
  "10.10.1.0/24",
  "10.10.2.0/24",
]

private_subnet_cidrs = [
  "10.10.11.0/24",
  "10.10.12.0/24",
]

tags = {
  Owner       = "alesz"
  CostCenter  = "personal-lab"
  Environment = "dev"
}

#EKS variables
cluster_suffix      = "eks"
authentication_mode = "API"
node_group_suffix   = "general"
node_instance_types = ["t3.medium"]

cluster_version   = "1.35"
node_desired_size = 2
node_min_size     = 1
node_max_size     = 3