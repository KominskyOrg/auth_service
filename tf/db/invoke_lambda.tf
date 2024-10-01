resource "null_resource" "invoke_manage_db_resources" {
  provisioner "local-exec" {
    command = <<EOT
      aws lambda invoke \
        --function-name ${var.manage_db_resources_lambda_arn} \
        --payload '{"stack_name": "${var.stack_name}", "env": "${var.env}"}' \
        --cli-binary-format raw-in-base64-out \
        response.json
    EOT
    environment = {
      AWS_DEFAULT_REGION = "us-east-1"
    }
  }

  triggers = {
    stack_name = var.stack_name
  }
}