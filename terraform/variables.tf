variable "github_token" {
  description = "GitHub Personal Access Token (PAT)"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub repository owner/organization"
  type        = string
  default     = "digomes87"
}

variable "repository_name" {
  description = "GitHub repository name"
  type        = string
  default     = "FastAPI-like-a-Pro"
}

variable "codecov_token" {
  description = "Codecov token for coverage reports (optional)"
  type        = string
  default     = ""
  sensitive   = true
}
