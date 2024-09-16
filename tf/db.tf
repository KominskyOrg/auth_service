locals {
  rds_secrets = jsondecode(data.aws_secretsmanager_secret_version.rds_instance_secrets_version.secret_string)
}

data "aws_db_instance" "database" {
  db_instance_identifier = "${var.org}-${var.env}-db"
}

data "aws_secretsmanager_secret" "rds_instance_secrets" {
  name = var.rds_instance_secrets_name
}

data "aws_secretsmanager_secret_version" "rds_instance_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.rds_instance_secrets.id
}

provider "mysql" {
  endpoint              = data.aws_db_instance.database.endpoint
  username              = local.rds_secrets["username"]
  password              = local.rds_secrets["password"]
}

resource "mysql_database" "auth_db" {
  name = "auth_db"
}

resource "random_password" "auth_db_user_password" {
  length  = var.db_user_password_length
  special = var.db_user_password_special
}

# Create a Secrets Manager secret to store the auth_service user password
resource "aws_secretsmanager_secret" "auth_db_user_password" {
  name        = "${var.org}-${var.env}-auth_db_user_password"
  description = "Password for the ${var.env} auth_service database user"
  recovery_window_in_days = 0
}

# Store the generated password in Secrets Manager
resource "aws_secretsmanager_secret_version" "auth_db_user_password_version" {
  secret_id     = aws_secretsmanager_secret.auth_db_user_password.id
  secret_string = random_password.auth_db_user_password.result
}

resource "mysql_user" "auth_service_user" {
  user     = "${var.env}_auth_user"
  host     = "%"
  plaintext_password = aws_secretsmanager_secret_version.auth_db_user_password_version.secret_string

  depends_on = [mysql_database.auth_db]
}

resource "mysql_grant" "auth_service_grant" {
  user       = mysql_user.auth_service_user.user
  host       = mysql_user.auth_service_user.host
  database   = mysql_database.auth_db.name
  privileges = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "INDEX", "ALTER"]
  table      = "*.*"

  depends_on = [mysql_user.auth_service_user]
}
