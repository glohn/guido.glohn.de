# Credentials come from the environment, e.g. `export AWS_PROFILE=priv`.

provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.tags
  }
}

# CloudFront only accepts ACM certificates from us-east-1.
provider "aws" {
  alias               = "us_east_1"
  region              = "us-east-1"
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.tags
  }
}

locals {
  name = replace(var.domain_name, ".", "-")

  tags = {
    Project   = var.domain_name
    ManagedBy = "opentofu"
  }
}
