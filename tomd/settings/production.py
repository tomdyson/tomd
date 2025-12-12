import os
from .base import *

DEBUG = False

# AWS S3 Configuration
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

if 'AWS_S3_CUSTOM_DOMAIN' in env:
    AWS_S3_CUSTOM_DOMAIN = env['AWS_S3_CUSTOM_DOMAIN']
if 'MEDIA_URL' in env:
    MEDIA_URL = env['MEDIA_URL']

# Django 5.1+ uses STORAGES instead of deprecated DEFAULT_FILE_STORAGE
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}