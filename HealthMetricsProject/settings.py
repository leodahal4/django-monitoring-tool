ENABLE_REDIS_CHECK = True
ENABLE_DB_CHECK = True
ENABLE_CACHE_CHECK = False
ENABLE_MONGO_CHECK = False
# Add more configuration flags as needed

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
CACHE_LOCATION = 'unique-snowflake'
