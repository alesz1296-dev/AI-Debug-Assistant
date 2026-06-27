terraform {
  backend "s3" {
    bucket = "ai-debug-assistant-ada-bootstrap-tf-state-akirqi"
    key    = "envs/dev/terraform.tfstate"
    region = "us-east-1"
    # dynamodb_table = "ai-debug-assistant-ada-bootstrap-tf-lock" old implementation
    use_lockfile = true # new implementation of backend
    encrypt      = true
  }
}