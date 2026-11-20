# Certificate for the custom domain. Validated via a DNS record at Hetzner,
# which has to be created by hand (see output "hetzner_dns_records").

resource "aws_acm_certificate" "site" {
  provider = aws.us_east_1

  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Waits until ACM sees the validation record and issues the certificate.
resource "aws_acm_certificate_validation" "site" {
  provider = aws.us_east_1

  certificate_arn = aws_acm_certificate.site.arn

  timeouts {
    create = "60m"
  }
}
