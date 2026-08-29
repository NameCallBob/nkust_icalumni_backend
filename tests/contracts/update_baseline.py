#!/usr/bin/env python
"""重新產生 API 路由契約基準檔 `tests/contracts/routes_baseline.json`。

**只有在你「刻意」變更 API 介面或權限之後才該執行這支腳本**，並且要把產生的
diff 一起放進 PR 讓 reviewer 看見——那份 diff 就是「這次改動對外部介面與權限
造成了什麼影響」的完整說明。

    python -m tests.contracts.update_baseline
    # 或
    make baseline
"""
import json
import os
import pathlib
import sys

BASELINE_PATH = pathlib.Path(__file__).with_name("routes_baseline.json")


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings_test")
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

    import django

    django.setup()

    from tests.route_map import collect_routes

    routes = collect_routes()
    payload = {
        "_comment": (
            "API 路由契約基準檔——由 `python -m tests.contracts.update_baseline` 產生。"
            "請勿手動編輯。任何差異都代表對外介面或權限設定有變動。"
        ),
        "route_count": len(routes),
        "routes": {r.key: r.to_dict() for r in routes},
    }
    BASELINE_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    unprotected = [r.key for r in routes if r.is_unprotected]
    print(f"已寫入 {BASELINE_PATH}")
    print(f"  路由總數：{len(routes)}")
    print(f"  匿名可存取：{len(unprotected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
