resource "kubernetes_secret" "db_credentials" {
  metadata {
    name      = "${var.env}-${var.stack_name}-db-credentials"
    namespace = var.env
  }

  data = {
    db_username = local.db_credentials.username
    db_password = local.db_credentials.password
    db_name     = "${var.stack_name}_db"
    db_host     = var.db_host
    db_port     = var.db_port
  }

  depends_on = [null_resource.invoke_manage_db_resources]
}

data "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = "${var.env}_${var.stack_name}_db_credentials"

  depends_on = [null_resource.invoke_manage_db_resources]
}

locals {
  db_credentials = jsondecode(data.aws_secretsmanager_secret_version.db_credentials.secret_string)
}