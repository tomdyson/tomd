# Wagtail site for tomd.org

## Local setup

`workon wagtail-tomd`

## Run on Heroku

Needs these keys:

```
ALLOWED_HOSTS
SECRET_KEY     
DATABASE_URL
MEDIA_URL
AWS_ACCESS_KEY_ID
AWS_S3_CUSTOM_DOMAIN
AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME
BUILD_DIR
NETLIFY_SITE_ID
NETLIFY_TOKEN
```

## Deploy to Netlify

`heroku run make build`

## Todo

 - [x] Blog home and details models
 - [x] Base styles using Tachyons
 - [ ] Download Source Serif Pro, which now has italics.
    - https://github.com/adobe-fonts/source-serif-pro