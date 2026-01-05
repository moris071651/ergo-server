import os
import toml

data = {}
try:
    with open('config.toml') as f:
        data = toml.load(f)
except Exception as e:
    pass

jwt_cfg = data.get("jwt", {})
JWT_SECRET_KEY = jwt_cfg.get("secret_key", "super-secret-key")
JWT_ALGORITHM = jwt_cfg.get("algorithm", "HS256")
JWT_EXPIRE_MINUTES = jwt_cfg.get("expire_minutes", 60)

auth_cookie_cfg = data.get("auth_cookie", {})
AUTH_COOKIE_KEY = auth_cookie_cfg.get("key", "ErgoAuthToken")
AUTH_COOKIE_HTTPONLY = auth_cookie_cfg.get("httponly", False)
AUTH_COOKIE_SECURE = auth_cookie_cfg.get("secure", True)
AUTH_COOKIE_SAMESITE = auth_cookie_cfg.get("samesite", "lax")
AUTH_COOKIE_MAX_AGE = auth_cookie_cfg.get("max_age", 3600)

redis_cfg = data.get("redis", {})
REDIS_URL = os.getenv("REDIS_URL", redis_cfg.get("url", "redis://localhost:6379/0"))
REDIS_LOGOUT_SET = redis_cfg.get("logout_set", "revoked_tokens")

database_cfg = data.get("database", {})
DATABASE_URL = os.getenv("DATABASE_URL", database_cfg.get("url", "postgresql+psycopg2://postgres:postgres@localhost:5432/app_db"))
DATABASE_ECHO = database_cfg.get("echo", True)
DATABASE_FUTURE = database_cfg.get("future", True)

bucket_cfg = data.get("bucket", {})
BUCKET_USER_PICTURE = bucket_cfg.get("user_picture", "user-picture")
BUCKET_LISTING_IMAGES = bucket_cfg.get("listing_images", "listing-images")

storage_cfg = data.get("storage", {})
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", storage_cfg.get("provider", "minio"))
STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT", storage_cfg.get("endpoint"))

s3_cfg = storage_cfg.get("aws", {})
STORAGE_AWS_REGION = os.getenv("AWS_REGION", s3_cfg.get("region", "us-east-1"))
STORAGE_AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", s3_cfg.get("access_key", "minioadmin"))
STORAGE_AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", s3_cfg.get("secret_key", "minioadmin"))

stripe_cfg = data.get("stripe", {})
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", stripe_cfg.get("secret_key", None))
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", stripe_cfg.get("webhook_secret", None))
