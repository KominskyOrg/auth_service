resource "aws_ecr_repository" "ecr_repo" {
  name                 = "${local.stack_name}_${local.microservice_type}_${var.env}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
