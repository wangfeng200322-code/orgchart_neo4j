Terraform demo

This Terraform is a minimal example that creates a single EC2 instance and runs a user-data script to clone this repository and start the docker-compose stack.

WARNING: This is for demo/test only. It creates an EC2 instance in your account and will incur charges.

Usage:
1. Configure AWS credentials (environment or profile).
2. Edit `terraform/terraform.tfvars` or pass variables at `terraform apply` time.
3. `terraform init && terraform apply`.

You will need to provide:
- `key_name` — an existing EC2 key pair in the target region so you can SSH.
- `repo_url` — this repository clone URL (defaults to the GitHub repo).

The user-data script expects Docker and docker-compose to be installed and will run `docker compose up -d`.