variable "region" {
  type = string
  default = "us-east-1"
}

variable "instance_type" {
  type = string
  default = "t2.micro"
}

variable "key_name" {
  type = string
}

variable "repo_url" {
  type = string
  default = "https://github.com/wangfeng200322-code/orgchart_neo4j.git"
}
