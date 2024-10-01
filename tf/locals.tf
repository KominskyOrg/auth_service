locals {
  tags = {
    env     = var.env
    service = "${local.stack_name}_${local.microservice_type}"
  }
  stack_name        = "auth"
  microservice_type = "service"
}