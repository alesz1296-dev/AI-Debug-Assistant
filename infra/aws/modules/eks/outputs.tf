output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = aws_eks_cluster.this.name
}

output "cluster_arn" {
  description = "ARN of the EKS cluster."
  value       = aws_eks_cluster.this.arn
}

output "cluster_endpoint" {
  description = "Endpoint for the EKS Kubernetes API server."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded certificate data required to communicate with the EKS cluster."
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "cluster_version" {
  description = "Kubernetes version running on the EKS control plane."
  value       = aws_eks_cluster.this.version
}

output "cluster_iam_role_arn" {
  description = "ARN of the IAM role used by the EKS control plane."
  value       = aws_iam_role.cluster.arn
}

output "node_group_name" {
  description = "Name of the managed EKS node group."
  value       = aws_eks_node_group.this.node_group_name
}

output "node_group_arn" {
  description = "ARN of the managed EKS node group."
  value       = aws_eks_node_group.this.arn
}

output "node_group_status" {
  description = "Current status of the managed EKS node group."
  value       = aws_eks_node_group.this.status
}

output "node_group_iam_role_arn" {
  description = "ARN of the IAM role used by the managed node group."
  value       = aws_iam_role.node_group.arn
}