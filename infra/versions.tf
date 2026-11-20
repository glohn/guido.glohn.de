terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # State stays local for now (infra/terraform.tfstate, not committed).
  # To move it to S3 later: create a state bucket, uncomment, run `tofu init -migrate-state`.
  #backend "s3" {
  #  bucket       = "tfstate-ACCOUNT_ID-eu-central-1"
  #  key          = "guido.glohn.de/terraform.tfstate"
  #  region       = "eu-central-1"
  #  use_lockfile = true
  #  encrypt      = true
  #}

  backend "local" {
    path = "terraform.tfstate"
  }
}
