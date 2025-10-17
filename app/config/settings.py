import toml

data = None
with open('config.toml') as f:
    data = toml.load()

jwt_cfg = data.get("jwt", {})
JWT_SECRET_KEY = jwt_cfg.get("secret_key", "super-secret-key")
JWT_ALGORITHM = jwt_cfg.get("algorithm", "HS256")
JWT_EXPIRE_MINUTES = jwt_cfg.get("expire_minutes", 60)

auth_cookie_cfg = data.get("auth_cookie", {})
AUTH_COOKIE_KEY = auth_cookie_cfg.get("key", "ErgoAuthToken")
AUTH_COOKIE_HTTPONLY = auth_cookie_cfg.get("httponly", True)
AUTH_COOKIE_SECURE = auth_cookie_cfg.get("secure", True)
AUTH_COOKIE_SAMESITE = auth_cookie_cfg.get("samesite", "lax")
AUTH_COOKIE_MAX_AGE = auth_cookie_cfg.get("max_age", 3600)

redis_cfg = data.get("redis", {})
REDIS_URL = redis_cfg.get("url", "redis://localhost:6379/0")
REDIS_LOGOUT_SET = redis_cfg.get("logout_set", "revoked_tokens")

database_cfg = data.get("database", {})
DATABASE_URL = database_cfg.get("url", "redis://localhost:6379/0")
DATABASE_ECHO = database_cfg.get("echo", True)
DATABASE_FUTURE = database_cfg.get("future", True)
