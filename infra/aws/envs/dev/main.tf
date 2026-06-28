locals {
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