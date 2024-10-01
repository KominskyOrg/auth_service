terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.11.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = local.tags
  }
}

data "aws_eks_cluster" "cluster" {
  name = data.terraform_remote_state.infrastructure.outputs.eks_cluster_name
}

data "aws_eks_cluster_auth" "cluster" {
  name = data.terraform_remote_state.infrastructure.outputs.eks_cluster_name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
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

module "eks" {
  source = "./eks"

  microservice_name = "${local.stack_name}-${local.microservice_type}"
  env               = var.env
  service_ecr_url   = aws_ecr_repository.ecr_repo.repository_url
  stack_name        = local.stack_name
  image_tag         = var.image_tag
}

module "db" {
  source = "./db"

  manage_db_resources_lambda_arn = data.terraform_remote_state.infrastructure.outputs.manage_db_resources_lambda_arn
  stack_name                     = local.stack_name
  env                            = var.env
  db_host                        = data.terraform_remote_state.infrastructure.outputs.db_host
  db_port                        = data.terraform_remote_state.infrastructure.outputs.db_port
}
