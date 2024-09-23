resource "kubernetes_secret" "db_credentials" {
  metadata {
    name      = "db-credentials"
    namespace = kubernetes_namespace.auth.metadata[0].name
  }

  data = {
    username = jsondecode(data.aws_secretsmanager_secret_version.rds_instance_secrets_version.secret_string)["username"]
    password = jsondecode(data.aws_secretsmanager_secret_version.rds_instance_secrets_version.secret_string)["password"]
  }
}