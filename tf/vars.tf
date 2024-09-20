# service_repos/auth_service/tf/variables.tf

variable "org" {
  description = "Organization name."
  type        = string
}

variable "env" {
  description = "Deployment environment (e.g., dev, prod)."
  type        = string
}

variable "db_user_password_length" {
  description = "Length of the generated database user password."
  type        = number
  default     = 16
}

variable "db_user_password_special" {
  description = "Include special characters in the generated password."
  type        = bool
  default     = true
}
