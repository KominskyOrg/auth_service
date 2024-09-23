resource "kubernetes_service" "auth_service" {
  metadata {
    name      = "auth-service"
    namespace = kubernetes_namespace.auth.metadata[0].name
  }

  spec {
    selector = {
      app = "auth-service"
    }

    port {
      port        = 80
      target_port = 5001
    }

    type = "ClusterIP"
  }
}