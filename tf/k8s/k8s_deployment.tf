resource "kubernetes_deployment" "auth_service" {
  metadata {
    name      = "auth-service"
    namespace = var.env
    labels = {
      app = "auth-service"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "auth-service"
      }
    }

    template {
      metadata {
        labels = {
          app = "auth-service"
        }
      }

      spec {
        container {
          name  = "auth-service"
          image = "${var.auth_service_ecr_url}:latest"

          port {
            container_port = 5001
          }

          env {
            name  = "DATABASE_URL"
            value = "mysql://$(username):$(password)@${data.aws_db_instance.database.endpoint}:3306/auth_db"
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.db_credentials.metadata[0].name
            }
          }
        }
      }
    }
  }
}