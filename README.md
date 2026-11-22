# guido.glohn.de

Personal link page: LinkedIn, GitHub, a contact card (vCard) and a QR code
to show on the phone at events. Static HTML on S3 + CloudFront (eu-central-1),
infrastructure with OpenTofu.

The site sets no cookies, has no tracking, loads nothing from other servers,
and CloudFront/S3 access logs are off.

## Layout

```
site/                 what gets deployed
  index.html          link page
  qr/index.html       full-screen QR code (keeps the screen on while shown)
  404.html
  guido-lohn.vcf      contact card            (generated)
  assets/             css, js, icons, images  (QR code, icons, og-card generated)
tools/
  make_assets.py      generates QR code, icons, preview card, vCard; imports a profile photo
  deploy.sh           uploads site/ to S3, invalidates CloudFront
infra/                OpenTofu: S3, CloudFront, ACM certificate
```

## Content changes

Edit `site/index.html`. Certifications show their expiry date like Credly
does: `Expires <date>` (class `valid`) or `Expired <date>`. `assets/certs.js`
switches `Expires` to `Expired` once the date in `<time datetime>` is reached,
so a lapsed certification is never shown as valid.

Name, title, URL and vCard links for the generated
files live at the top of `tools/make_assets.py`; regenerate with:

```sh
uv run tools/make_assets.py
uv run tools/make_assets.py --photo ~/Downloads/profile.jpg   # new profile photo
uv run tools/make_assets.py --photo ~/Downloads/profile.jpg --crop L,T,R,B   # use only a region
```

Current profile image: `blueprint_final.png` (1254 × 1254) with `--crop 137,40,1117,1020`.

Photos are cropped to a square, resized and saved without metadata. With a
real photo the vCard also gets the picture.

Privacy policy: `site/datenschutz/` (German, authoritative) and `site/privacy/`
(English). Keep both in sync with what the site and `glohn-mail` actually do
(hosting, price class, logs, mail forwarding, retention). There is deliberately
no Impressum.

Local preview: `python3 -m http.server -d site 8000`, then open http://localhost:8000.

Deploy:

```sh
AWS_PROFILE=priv tools/deploy.sh
```

`deploy.sh` refuses to upload while `TODO` placeholders are left in the HTML.

## First-time setup

```sh
export AWS_PROFILE=priv
cd infra
cp account.auto.tfvars.example account.auto.tfvars   # fill in the account ID (git-ignored)
tofu init

# 1. Certificate first, to get its DNS validation record
tofu apply -target=aws_acm_certificate.site
tofu output acm_validation_records      # create this CNAME in the Hetzner zone glohn.de

# 2. Everything else (waits until ACM has validated the certificate)
tofu apply
tofu output hetzner_dns_records         # create the CNAME guido -> <id>.cloudfront.net.

# 3. First upload
cd .. && tools/deploy.sh
```

## Notes

- The AWS account ID is not in the repository: it lives in the git-ignored
  `infra/account.auto.tfvars`. `allowed_account_ids` makes OpenTofu refuse
  to run against any other account.
- The OpenTofu state is local (`infra/terraform.tfstate`, git-ignored).
  `infra/versions.tf` has a commented S3 backend for moving it.
- Should glohn.de ever get a CAA record, it must allow `amazon.com`,
  otherwise ACM cannot renew the certificate.
