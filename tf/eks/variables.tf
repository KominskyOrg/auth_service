variable "microservice_name" {
  description = "Microservice name"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag for microservice"
  type        = string
  default     = "latest"
}

variable "replicas" {
  description = "Number of replicas for microservice deployment"
  type        = number
  default     = 1
}

variable "env" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "service_ecr_url" {
  description = "Microservice ECR repository URL"
  type        = string
}

variable "stack_name" {
  description = "Microservice stack name"
  type        = string
}