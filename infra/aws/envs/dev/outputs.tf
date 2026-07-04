output "vpc_id" {
  description = "ID of the dev VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the dev public subnets."
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the dev private subnets."
  value       = module.network.private_subnet_ids
}

output "internet_gateway_id" {
  description = "ID of the dev internet gateway."
  value       = module.network.internet_gateway_id
}

output "nat_gateway_id" {
  description = "ID of the dev NAT gateway when enabled."
  value       = module.network.nat_gateway_id
}

output "ecr_repository_name" {
  description = "Name of the dev ECR repository."
  value       = module.ecr.repository_name
}

output "ecr_repository_url" {
  description = "URL of the dev ECR repository."
  value       = module.ecr.repository_url
}

output "ecr_repository_arn" {
  description = "ARN of the dev ECR repository."
  value       = module.ecr.repository_arn
}

output "eks_enabled" {
  description = "Whether the short-lived dev EKS lab is enabled."
  value       = var.enable_eks
}

output "eks_subnet_tier" {
  description = "Subnet tier selected for the dev EKS lab."
  value       = var.eks_subnet_tier
}

output "eks_cluster_name" {
  description = "Name of the dev EKS cluster when enabled."
  value       = try(module.eks[0].cluster_name, null)
}

output "eks_cluster_endpoint" {
  description = "Endpoint of the dev EKS cluster when enabled."
  value       = try(module.eks[0].cluster_endpoint, null)
}

output "eks_node_group_name" {
  description = "Name of the dev EKS managed node group when enabled."
  value       = try(module.eks[0].node_group_name, null)
}

output "eks_node_group_status" {
  description = "Status of the dev EKS managed node group when enabled."
  value       = try(module.eks[0].node_group_status, null)
}
