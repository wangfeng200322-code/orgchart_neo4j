variable "region" {
  type = string
  default = "eu-central-1"
}

variable "instance_type" {
  type = string
  default = "t2.micro"
}

variable "key_name" {
  type = "my_ec2_key_pair-2025"
}

variable "repo_url" {
  type = string
  default = "https://github.com/wangfeng200322-code/orgchart_neo4j.git"
}
