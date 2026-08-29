"""API 路由契約：介面與權限只要有變動就會失敗。

這支測試不判斷「好或壞」，它只回答一個問題：
**這次改動有沒有動到對外的 API 介面或權限設定？**

對公開 repo 來說這件事特別重要——外部貢獻者送的 PR 可能無心之間把某支端點的
`permission_classes` 從 `IsAdminUser` 改成 `AllowAny`，或新增了一支忘了加權限的
端點。人工 review 幾百行 diff 很容易漏看；這支測試會把它變成一行清楚的失敗訊息。

失敗時的處理流程：

1. 讀失敗訊息列出的差異，確認**每一項都是你刻意做的**。
2. 若是刻意的：``make baseline``（或 ``python -m tests.contracts.update_baseline``）
   重新產生基準檔，並把 diff 一併提交，讓 reviewer 看見介面變動。
3. 若不是刻意的：那就是這支測試抓到 bug 了，去修程式碼。
"""
import json
import pathlib

import pytest

from tests.route_map import collect_routes

pytestmark = pytest.mark.contract

BASELINE_PATH = pathlib.Path(__file__).with_name("routes_baseline.json")

REGENERATE_HINT = (
    "\n\n若以上變動是刻意的，請執行 `make baseline`（或 "
    "`python -m tests.contracts.update_baseline`）更新基準檔，並將 diff 一併提交。"
)


@pytest.fixture(scope="module")
def baseline():
    if not BASELINE_PATH.exists():
        pytest.fail(
            f"找不到路由基準檔 {BASELINE_PATH}。"
            "首次建立請執行 `python -m tests.contracts.update_baseline`。"
        )
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["routes"]


@pytest.fixture(scope="module")
def current():
    return {r.key: r.to_dict() for r in collect_routes()}


def test_no_endpoint_was_added_without_updating_the_contract(current, baseline):
    added = sorted(set(current) - set(baseline))
    assert not added, (
        f"偵測到 {len(added)} 支未登記於契約的新端點：\n"
        + "\n".join(
            f"  + {key}  權限={current[key]['permissions'] or '【無權限檢查】'}"
            for key in added
        )
        + REGENERATE_HINT
    )


def test_no_endpoint_disappeared(current, baseline):
    removed = sorted(set(baseline) - set(current))
    assert not removed, (
        f"偵測到 {len(removed)} 支端點消失——前端或既有整合可能因此壞掉：\n"
        + "\n".join(f"  - {key}" for key in removed)
        + REGENERATE_HINT
    )


def test_no_endpoint_changed_its_security_settings(current, baseline):
    """權限／認證／節流設定的變動必須是刻意且被 review 過的。"""
    changes = []
    for key in sorted(set(current) & set(baseline)):
        now, before = current[key], baseline[key]
        for field in ("permissions", "authentication", "throttle_scope", "view"):
            if now[field] != before[field]:
                changes.append(f"  ~ {key}\n      {field}: {before[field]} → {now[field]}")

    assert not changes, (
        f"偵測到 {len(changes)} 項端點安全設定變動：\n" + "\n".join(changes) + REGENERATE_HINT
    )


def test_public_surface_did_not_grow(current, baseline):
    """匿名可存取的端點清單是攻擊面本身——擴大必須被明確看見。

    這條與上面那條有重疊，但刻意分開：權限 class 換名字（例如 IsAdminUser →
    IsStaffPermission）跟「這支端點從此對全世界開放」是兩種嚴重程度完全不同的
    事，混在同一個失敗訊息裡會被忽略。
    """

    def is_public(entry):
        perms = entry["permissions"]
        return not perms or set(perms) <= {"AllowAny"}

    newly_public = sorted(
        key
        for key in set(current) & set(baseline)
        if is_public(current[key]) and not is_public(baseline[key])
    )
    assert not newly_public, (
        f"偵測到 {len(newly_public)} 支端點從『需要授權』變成『匿名可存取』：\n"
        + "\n".join(
            f"  ! {key}\n      {baseline[key]['permissions']} → "
            f"{current[key]['permissions'] or '【無權限檢查】'}"
            for key in newly_public
        )
        + "\n\n這會直接擴大攻擊面。請確認這是刻意的資料公開決策，"
        + "並確認該端點回傳的欄位不含個資（見 tests/security/test_pii_leakage.py）。"
        + REGENERATE_HINT
    )


def test_baseline_route_count_matches(current, baseline):
    """基準檔本身沒有被手動改壞。"""
    declared = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["route_count"]
    assert declared == len(baseline), (
        "基準檔的 route_count 與實際 routes 數量不一致，代表它被手動編輯過。"
        "請改用 `make baseline` 重新產生。"
    )
