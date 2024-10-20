import os
import glob

# 指定你的應用目錄路徑
apps_dir = '../apps'

# 刪除所有遷移文件，但保留 __init__.py
for root, dirs, files in os.walk(apps_dir):
    if 'migrations' in dirs:
        migration_dir = os.path.join(root, 'migrations')
        for file in glob.glob(os.path.join(migration_dir, '*.py')):
            if not file.endswith('__init__.py'):
                os.remove(file)
        for file in glob.glob(os.path.join(migration_dir, '*.pyc')):
            os.remove(file)

print("已刪除所有遷移文件。")