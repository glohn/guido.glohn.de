variable "aws_account_id" {
  description = "AWS account to deploy into (guards against the wrong profile). Set in account.auto.tfvars, which is git-ignored."
  type        = string
}

variable "aws_region" {
  description = "Region for the S3 bucket."
  type        = string
  default     = "eu-central-1"
}

variable "domain_name" {
  description = "Public hostname of the site."
  type        = string
}

variable "dns_zone" {
  description = "DNS zone at Hetzner that contains domain_name. Used to print relative record names."
  type        = string
}

variable "price_class" {
  description = "CloudFront price class. PriceClass_100 = North America, Europe, Israel."
  type        = string
  default     = "PriceClass_100"
}
