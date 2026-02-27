"""CORS 配置"""
ALLOWED_ORIGINS = [
    "https://medroundtable-v2.vercel.app",
    "https://medroundtable.zeabur.app",
    "https://*.zeabur.app",
]

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]

ALLOWED_HEADERS = [
    "*",
    "Authorization",
    "Content-Type",
    "X-Request-ID",
    "X-Correlation-ID",
]
