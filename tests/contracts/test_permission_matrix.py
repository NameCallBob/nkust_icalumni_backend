"""權限矩陣：對每一條路由實際發出匿名請求，驗證它真的擋得住。

與 `test_route_inventory.py` 的差別很關鍵：

* `test_route_inventory` 檢查的是**宣告**——原始碼上寫了什麼 permission class。
* 這一支檢查的是**行為**——真的送一個沒有憑證的 HTTP 請求進去，看它回什麼。

兩者會抓到不同的 bug。宣告正確但行為錯誤的情況實際存在，例如：view 覆寫了
`get_permissions()`、`@action` 的 decorator 被寫在錯誤的位置、或某個自訂
permission class 在 `request.user` 為匿名時丟出例外而被吞掉。只看原始碼看不出來。

路由分三類處理：

===================  ==========================================================
分類                 匿名請求的預期行為
===================  ==========================================================
完全受保護           所有動詞都必須被擋（401/403）
唯讀公開             GET 可通過；POST/PUT/PATCH/DELETE 必須被擋
完全公開             不驗證權限，只驗證「不得 5xx」
===================  ==========================================================
"""
import pytest

from tests.helpers import (
    ALL_METHODS,
    DENIED_STATUSES,
    NOT_APPLICABLE_STATUSES,
    SAFE_METHODS,
    concrete_url,
)
from tests.route_map import collect_routes

pytestmark = [pytest.mark.contract, pytest.mark.security, pytest.mark.django_db]

_ALL_ROUTES = collect_routes()
PROTECTED_ROUTES = [r for r in _ALL_ROUTES if not r.is_unprotected and not r.is_read_open]
READ_OPEN_ROUTES = [r for r in _ALL_ROUTES if r.is_read_open]
PUBLIC_ROUTES = [r for r in _ALL_ROUTES if r.is_unprotected]

# ── 已知技術債：permission_classes 是空清單（等同無權限檢查）─────────────────
#
# 這些是接手時就存在的狀態，不是本次測試體系引入的。列在這裡的用意是：
# **凍結現況**——既有的四支不讓 CI 紅到大家把測試關掉，但只要再多出第一支新的，
# 測試就會失敗。清單只能變短，不能變長。
#
# 修法：若確定要公開，改寫成 `permission_classes=[permissions.AllowAny]`，
# 把「公開」變成一個看得見、review 得到的決定；並補上 PII 外洩測試。
KNOWN_UNDECLARED_PERMISSIONS = frozenset(
    {
        # DRF SimpleJWT 內建 view，本來就設計為公開；此處只是沒有顯式宣告。
        "api/token/verify/::-",
        # 前台職缺頁使用，實務上確實需要公開，但應改為顯式 AllowAny。
        "recruit/data/all_active/::GET",
        "recruit/data/getOne/::GET",
        "recruit/data/tableOutput/::GET",
    }
)


def _methods_for(route):
    """route 有 router actions 就用它；APIView 沒有，只能全動詞試一輪。"""
    return [m.lower() for m in route.methods] if route.methods else list(ALL_METHODS)


def _probe(client, route, methods):
    """對指定動詞逐一發出匿名請求，回傳 [(動詞, 狀態碼)]。"""
    url = concrete_url(route.path)
    return [(m.upper(), getattr(client, m)(url).status_code) for m in methods]


@pytest.mark.parametrize("route", PROTECTED_ROUTES, ids=lambda r: r.key)
def test_anonymous_request_is_rejected(anon_client, route):
    """匿名請求打受保護端點，一律必須被擋（401/403）。"""
    results = _probe(anon_client, route, _methods_for(route))
    failures = [
        f"{method} {concrete_url(route.path)} → {status}"
        for method, status in results
        if status not in DENIED_STATUSES and status not in NOT_APPLICABLE_STATUSES
    ]

    assert not failures, (
        f"端點 {route.key}（宣告權限 {list(route.permissions)}）未擋下匿名請求：\n"
        + "\n".join(f"  {f}" for f in failures)
        + "\n\n預期 401/403。回 2xx 代表未授權存取；回 5xx 代表權限檢查前就炸了"
        "（同樣是問題，攻擊者可用來探測內部錯誤）。"
    )


@pytest.mark.parametrize("route", READ_OPEN_ROUTES, ids=lambda r: r.key)
def test_read_open_endpoint_still_rejects_anonymous_writes(anon_client, route):
    """唯讀公開的端點，寫入動詞仍必須擋下匿名。

    `IsAdminOrReadOnly` / `IsAuthenticatedOrReadOnly` 這類權限最容易出事的地方，
    是它只看 `request.method`——只要有人在 view 上加了一個 `@action(methods=['get'])`
    卻在裡面做寫入，安全動詞的豁免就變成了未授權寫入。
    """
    write_methods = [m for m in _methods_for(route) if m.upper() not in SAFE_METHODS]
    if not write_methods:
        pytest.skip("此路由沒有寫入動詞")

    results = _probe(anon_client, route, write_methods)
    failures = [
        f"{method} {concrete_url(route.path)} → {status}"
        for method, status in results
        if status not in DENIED_STATUSES and status not in NOT_APPLICABLE_STATUSES
    ]

    assert not failures, (
        f"唯讀公開端點 {route.key}（{list(route.permissions)}）未擋下匿名寫入：\n"
        + "\n".join(f"  {f}" for f in failures)
    )


@pytest.mark.parametrize(
    "route", PUBLIC_ROUTES + READ_OPEN_ROUTES, ids=lambda r: r.key
)
def test_public_endpoint_does_not_crash_for_anonymous(anon_client, route):
    """公開端點面對「什麼參數都沒帶」的匿名請求不得 5xx。

    公開端點是唯一不需要任何憑證就能觸及的程式碼，也是最常被掃描器打的地方。
    缺少必填參數時應該回 400/404 這類明確的客戶端錯誤，而不是未處理例外——
    後者會把 traceback 與內部結構洩漏給任何人，也是最容易被做成 DoS 的入口。
    """
    results = _probe(anon_client, route, _methods_for(route))
    failures = [
        f"{method} {concrete_url(route.path)} → {status}"
        for method, status in results
        if status >= 500
    ]

    assert not failures, (
        f"公開端點 {route.key} 在沒有參數的匿名請求下發生伺服器錯誤：\n"
        + "\n".join(f"  {f}" for f in failures)
        + "\n\n請改為回傳 400（參數錯誤）或 404（找不到資源）。"
    )


def test_no_new_route_omits_its_permission_declaration():
    """不得再新增「permission_classes 是空清單」的路由。

    `permission_classes=[]` 與 `[AllowAny]` 執行結果相同，但意圖完全不同：前者
    通常是「複製貼上時把清單清空了」，後者是「我確定這要公開」。這條測試強迫
    公開必須是一個寫得出來、review 得到的決定。

    既有的例外見 `KNOWN_UNDECLARED_PERMISSIONS`——那份清單只能變短。
    """
    undeclared = {r.key for r in _ALL_ROUTES if not r.permissions}
    new_offenders = sorted(undeclared - KNOWN_UNDECLARED_PERMISSIONS)

    assert not new_offenders, (
        "以下路由的 permission_classes 是空清單，等同完全沒有權限檢查：\n"
        + "\n".join(f"  {k}" for k in new_offenders)
        + "\n\n若確定要公開，請明確寫成 `permission_classes=[permissions.AllowAny]`。"
    )


def test_known_permission_debt_list_is_not_stale():
    """技術債清單裡的項目修好之後，要記得把它從清單移除。

    沒有這條，`KNOWN_UNDECLARED_PERMISSIONS` 會變成永遠沒人整理的墓地，
    最後失去「清單只能變短」的意義。
    """
    undeclared = {r.key for r in _ALL_ROUTES if not r.permissions}
    already_fixed = sorted(KNOWN_UNDECLARED_PERMISSIONS - undeclared)

    assert not already_fixed, (
        "以下路由已經補上顯式權限宣告，請從 KNOWN_UNDECLARED_PERMISSIONS 移除：\n"
        + "\n".join(f"  {k}" for k in already_fixed)
    )
