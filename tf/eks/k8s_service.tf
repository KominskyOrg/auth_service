resource "kubernetes_service" "k8s_service" {
  metadata {
    name      = var.microservice_name 
    namespace = var.env
  }

  spec {
    selector = {
      app = var.microservice_name
    }

    port {
      port        = 8080
      target_port = 5001
    }

    type = "ClusterIP"
  }
}