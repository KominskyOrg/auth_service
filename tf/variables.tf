variable "image_tag" {
  description = "Docker image tag for auth_app"
  type        = string
  default     = "latest"
}

variable "replicas" {
  description = "Number of replicas for auth_app deployment"
  type        = number
  default     = 1
}

variable "env" {
  description = "Environment name"
  type        = string
  default     = "staging"
}