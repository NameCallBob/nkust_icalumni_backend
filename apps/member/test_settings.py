"""相容用 shim：測試設定已移至 `tests/settings_test.py`。

保留這個模組是因為既有的指令、CI 設定與文件都寫著
`DJANGO_SETTINGS_MODULE=apps.member.test_settings`。新的設定加在
`tests/settings_test.py`，不要加在這裡。
"""
from tests.settings_test import *  # noqa: F401,F403
