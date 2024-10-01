resource "kubernetes_deployment" "k8s_deployment" {
  metadata {
    name      = "${var.microservice_name}"
    namespace = var.env
    labels = {
      app = "${var.microservice_name}"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "${var.microservice_name}"
      }
    }

    template {
      metadata {
        labels = {
          app = "${var.microservice_name}"
        }
      }

      spec {
        container {
          name  = "${var.microservice_name}"
          image = "${var.service_ecr_url}:${var.image_tag}"

          port {
            container_port = 5001
          }

          env_from {
            secret_ref {
              name = "${var.env}-${var.stack_name}-db-credentials"
            }
          }
        }
      }
    }
  }
}