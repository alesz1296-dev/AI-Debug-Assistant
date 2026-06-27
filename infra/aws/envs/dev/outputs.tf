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
  description = "ID of the dev NAT gateway."
  value       = module.network.nat_gateway_id
}
