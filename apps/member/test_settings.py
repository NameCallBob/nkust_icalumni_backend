"""測試專用設定"""
from IC_alumni.settings import *

# 使用 SQLite 作為測試資料庫
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 關閉 DEBUG 模式以獲得更真實的測試環境
DEBUG = False

# 簡化密碼驗證器以加快測試速度
AUTH_PASSWORD_VALIDATORS = []