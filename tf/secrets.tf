# service_repos/auth_service/tf/secrets.tf

# Data source to retrieve the auth_service user password from AWS Secrets Manager (Production)
data "aws_secretsmanager_secret_version" "auth_db_user_password_prod" {
  count     = var.env == "prod" ? 1 : 0
  secret_id = aws_secretsmanager_secret.auth_db_user_password.id
}

# Local variable to conditionally assign password
locals {
  auth_service_user_password = var.env == "prod" ? data.aws_secretsmanager_secret_version.auth_db_user_password_prod[0].secret_string : random_password.auth_db_user_password.result
}
