terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    mysql = {
      source = "petoju/mysql"
      version = "~> 3.0"
    }
  }

  # backend "s3" {
  #   bucket         = "${var.org}-${var.env}-tf-statelock"
  #   key            = "auth_service.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "tf-state-table"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = "us-east-1"
}

locals {
  org = "kominskyorg"
  env = "dev"
  cluster_name = "${var.org}-${var.env}-cluster"
}

data "terraform_remote_state" "infrastructure" {
  backend = "s3"
  config = {
    bucket         = "tf-statelock"
    key            = "kom_aws_tf.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-state-table"
  }
}
