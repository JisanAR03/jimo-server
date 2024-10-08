import os
from typing import Optional

# Database connection URL (async)
# Example: "postgresql+asyncpg://user@localhost/jimo_db"
SQLALCHEMY_DATABASE_URL: str = os.environ["DATABASE_URL"]

# If specified, new posts will send a Slack message using the given webhook URL.
# Example: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
SLACK_HOOK: Optional[str] = os.environ.get("SLACK_HOOK")

# Allow requests from this origin
ALLOW_ORIGIN: Optional[str] = os.environ.get("ALLOW_ORIGIN")

# If true, enable docs and openapi.json endpoints
ENABLE_DOCS: bool = os.environ.get("ENABLE_DOCS") == "1"

# Firebase storage bucket for user images
STORAGE_BUCKET: str = os.environ.get("STORAGE_BUCKET", "goodplaces-app.appspot.com")

# Cloudflare R2 storage configuration
R2_ENDPOINT_URL: str = os.environ.get("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID: str = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY: str = os.environ.get("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME: str = os.environ.get("R2_BUCKET_NAME")
R2_PUBLIC_ENDPOINT: str = os.environ.get("R2_PUBLIC_ENDPOINT")