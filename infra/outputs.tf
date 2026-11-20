locals {
  zone_suffix = ".${var.dns_zone}."

  acm_validation_records = [
    for o in aws_acm_certificate.site.domain_validation_options : {
      name  = trimsuffix(o.resource_record_name, local.zone_suffix)
      type  = o.resource_record_type
      value = o.resource_record_value
    }
  ]
}

output "hetzner_dns_records" {
  description = "Records to create in the Hetzner DNS zone (names relative to the zone)."
  value = concat(local.acm_validation_records, [{
    name  = trimsuffix("${var.domain_name}.", local.zone_suffix)
    type  = "CNAME"
    value = "${aws_cloudfront_distribution.site.domain_name}."
  }])
}

output "acm_validation_records" {
  description = "Only the certificate validation record(s); available after the first (targeted) apply."
  value       = local.acm_validation_records
}

output "bucket_name" {
  value = aws_s3_bucket.site.id
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.site.id
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.site.domain_name
}
