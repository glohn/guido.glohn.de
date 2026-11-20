#!/usr/bin/env bash
# Upload site/ to S3 and clear the CloudFront cache.
#
# Usage: AWS_PROFILE=priv tools/deploy.sh [BUCKET DISTRIBUTION_ID]
#
# Without arguments, bucket and distribution are read from `tofu output`.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site="$root/site"
cache="public, max-age=300"

if grep -rn --include='*.html' 'TODO' "$site"; then
  echo "Refusing to deploy: placeholders (TODO) left in site/." >&2
  exit 1
fi

bucket="${1:-$(tofu -chdir="$root/infra" output -raw bucket_name)}"
distribution="${2:-$(tofu -chdir="$root/infra" output -raw cloudfront_distribution_id)}"

aws s3 sync "$site/" "s3://$bucket/" --delete --no-progress --exclude "*.vcf" --cache-control "$cache"

# Set the vCard type explicitly so phones offer "add to contacts".
for vcf in "$site"/*.vcf; do
  aws s3 cp --no-progress "$vcf" "s3://$bucket/$(basename "$vcf")" \
    --content-type "text/vcard; charset=utf-8" --cache-control "$cache"
done

echo "Invalidation: $(aws cloudfront create-invalidation --distribution-id "$distribution" \
  --paths "/*" --query 'Invalidation.Id' --output text)"
