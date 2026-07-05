param(
    [string]$AwsRegion = "us-east-1",
    [string]$AwsAccountId = "",
    [string]$RepositoryName = "ai-debug-assistant-ada-dev-api",
    [string]$ImageTag = "dev",
    [string]$LocalImageName = "ai-debug-assistant-api",
    [string]$DockerfilePath = "infra/Dockerfile.api",
    [string]$BuildContext = "."
)

$ErrorActionPreference = "Stop"

Write-Host "Checking AWS identity..."
$CallerIdentity = aws sts get-caller-identity | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($AwsAccountId)) {
    $AwsAccountId = $CallerIdentity.Account
}

$Registry = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$LocalImage = "${LocalImageName}:${ImageTag}"
$EcrImage = "${Registry}/${RepositoryName}:${ImageTag}"

Write-Host "Using AWS account: $AwsAccountId"
Write-Host "Using AWS region: $AwsRegion"
Write-Host "Using ECR repository: $RepositoryName"
Write-Host "Using image tag: $ImageTag"

Write-Host "Checking ECR repository..."
aws ecr describe-repositories `
    --region $AwsRegion `
    --repository-names $RepositoryName | Out-Null

Write-Host "Logging Docker into ECR..."
aws ecr get-login-password --region $AwsRegion |
    docker login `
        --username AWS `
        --password-stdin $Registry

Write-Host "Building local Docker image: $LocalImage"
docker build `
    -f $DockerfilePath `
    -t $LocalImage `
    $BuildContext

Write-Host "Tagging image for ECR: $EcrImage"
docker tag $LocalImage $EcrImage

Write-Host "Pushing image to ECR..."
docker push $EcrImage

Write-Host "Verifying pushed image..."
aws ecr describe-images `
    --region $AwsRegion `
    --repository-name $RepositoryName `
    --image-ids imageTag=$ImageTag `
    --query "imageDetails[].{Tags:imageTags,Digest:imageDigest,PushedAt:imagePushedAt,Size:imageSizeInBytes}"

Write-Host "Done. Image pushed: $EcrImage"
