locals {
  eks_subnet_ids = var.eks_subnet_tier == "public" ? module.network.public_subnet_ids : module.network.private_subnet_ids

  common_tags = merge(
    {
      Project     = var.project_name
      App         = var.app_name
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags
  )
}

module "network" {
  source = "../../modules/network"

  project_name         = var.project_name
  app_name             = var.app_name
  environment          = var.environment
  tags                 = local.common_tags
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = var.enable_nat_gateway
}

module "ecr" {
  source = "../../modules/ecr"

  project_name         = var.project_name
  app_name             = var.app_name
  environment          = var.environment
  repository_suffix    = "api"
  image_tag_mutability = "MUTABLE" #Change to INMUTABLE in prod/staging
  scan_on_push         = true
  lifecycle_keep_count = 10
  tags                 = local.common_tags
}

resource "terraform_data" "cost_guardrails" {
  input = {
    enable_alb                = var.enable_alb
    enable_container_insights = var.enable_container_insights
    enable_eks                = var.enable_eks
    enable_elasticache        = var.enable_elasticache
    enable_nat_gateway        = var.enable_nat_gateway
    enable_rds                = var.enable_rds
    eks_subnet_tier           = var.eks_subnet_tier
  }

  lifecycle {
    precondition {
      condition     = !var.enable_eks || var.eks_subnet_tier != "private" || var.enable_nat_gateway
      error_message = "Private-subnet EKS labs require enable_nat_gateway = true. Use eks_subnet_tier = \"public\" for the lower-cost dev lab path."
    }
  }
}

# Cost-controlled dev rule:
# keep EKS, NAT, RDS, ElastiCache, ALB, and Container Insights disabled
# unless a short-lived lab intentionally enables them and records teardown proof.
module "eks" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/eks"

  project_name = var.project_name
  app_name     = var.app_name
  environment  = var.environment
  tags         = local.common_tags

  cluster_suffix      = var.cluster_suffix
  cluster_version     = var.cluster_version
  authentication_mode = var.authentication_mode

  subnet_ids = local.eks_subnet_ids

  node_group_suffix   = var.node_group_suffix
  node_instance_types = var.node_instance_types
  node_desired_size   = var.node_desired_size
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
}
