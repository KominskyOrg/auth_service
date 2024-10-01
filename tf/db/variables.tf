variable "stack_name" {
  description = "Name of the stack to initialize"
  type        = string
}

variable "manage_db_resources_lambda_arn" {
  description = "ARN of the manage_db_resources lambda function"
  type        = string
}

variable "env" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "db_host" {
  description = "Host of the database"
  type        = string
}

variable "db_port" {
  description = "Port of the database"
  type        = string
}