import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '1234'

    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://neondb_owner:npg_MNzq9LwiZV4r@ep-gentle-hill-aqzq5max-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    JSON_SORT_KEYS = False