"""URLconf 自省：把整份路由表變成可比對、可斷言的資料結構。

這是整套測試裡最重要的一塊。本專案有 200+ 條路由、權限散落在 ViewSet 屬性與
`@action(permission_classes=[...])` 兩處，靠人工 review 幾乎不可能保證「每一支
端點的權限都是刻意設定的」。這個模組在執行期把 Django 解析完的路由樹攤平，
連同每條路由**實際生效**的 permission/authentication class 一起取出，讓：

* `tests/contracts/test_route_inventory.py` 能與基準檔比對，任何端點的新增、
  移除、權限變動都會讓 CI 失敗並印出可讀的差異；
* `tests/contracts/test_permission_matrix.py` 能對每一條路由逐一發出匿名請求，
  驗證「沒有列在公開白名單裡的端點，匿名一律不得成功」。

取權限的順序刻意與 DRF 的 `initialize_request` 一致：
`@action` 的 `initkwargs` 優先，其次才是 view class 屬性，最後是全域預設。
"""
import re
from dataclasses import dataclass, field
from typing import Optional

from django.urls import URLPattern, URLResolver, get_resolver

# 這些 permission class 對「安全動詞」(GET/HEAD/OPTIONS) 放行匿名，對寫入動詞才要求授權。
# 契約與權限矩陣都必須知道這件事，否則會把「唯讀公開」誤判成「完全鎖住」。
READ_OPEN_PERMISSIONS = frozenset(
    {
        "IsAdminOrReadOnly",
        "IsAuthenticatedOrReadOnly",
        "DjangoModelPermissionsOrAnonReadOnly",
    }
)

ANONYMOUS_PERMISSIONS = frozenset({"AllowAny"})

# DRF 會在 ViewSet 首次被請求時，把 head 補進 as_view() 收下的那個 actions dict
# （而且是原地修改共用物件）。若把 HEAD/OPTIONS 一起收進契約，同一次 pytest 執行中
# 「先發過請求」與「沒發過請求」得到的路由清單會不一致，契約測試會隨執行順序時好時壞。
_DERIVED_METHODS = frozenset({"HEAD", "OPTIONS"})

# 這些路由不屬於本專案的 API 介面，不納入契約：
# - Django admin 自帶的數十條路由
# - DEBUG 下才掛載的靜態/媒體檔服務
# - drf-yasg 文件頁（僅在 EXPOSE_API_DOCS=1 時掛載）
EXCLUDED_PREFIXES = (
    "database/admin",
    "static/",
    "media/",
    "^static/",
    "^media/",
    "server/api/",
)


@dataclass(frozen=True)
class Route:
    """一條實際可被請求的路由，以及它實際生效的安全設定。"""

    path: str
    """正規化後的 URL（例：``member/any/getOne/``），不含前導斜線。"""

    methods: tuple = field(default=())
    """ViewSet router 產生的路由才有值（例：``("GET",)``）；APIView 為空 tuple。"""

    view: str = ""
    """view class 的完整名稱（``apps.member.views.MemberViewSet``）。"""

    permissions: tuple = field(default=())
    """實際生效的 permission class 名稱。空 tuple 代表**完全沒有權限檢查**。"""

    authentication: tuple = field(default=())
    """實際生效的 authentication class 名稱。"""

    throttle_scope: Optional[str] = None

    @property
    def key(self):
        """在基準檔中識別這條路由的唯一鍵。"""
        return f"{self.path}::{','.join(self.methods) or '-'}"

    @property
    def is_unprotected(self):
        """匿名可通過**所有**動詞的權限檢查（AllowAny，或根本沒有 permission class）。"""
        return not self.permissions or set(self.permissions) <= ANONYMOUS_PERMISSIONS

    @property
    def is_read_open(self):
        """匿名可讀、但寫入需要授權（`IsAdminOrReadOnly` 這類）。"""
        return bool(self.permissions) and set(self.permissions) <= READ_OPEN_PERMISSIONS

    @property
    def anonymously_readable(self):
        """匿名 GET 得到的資料會直接對外——PII 外洩測試的掃描範圍。"""
        return self.is_unprotected or self.is_read_open

    def to_dict(self):
        return {
            "path": self.path,
            "methods": list(self.methods),
            "view": self.view,
            "permissions": list(self.permissions),
            "authentication": list(self.authentication),
            "throttle_scope": self.throttle_scope,
        }


# regex 錨點只在「路徑段的開頭/結尾」才是錨點；出現在中間的 ^ 是字元類別的
# 否定符號（`[^/.]+`），一律砍掉會把 pk 的 pattern 改壞。
_ANCHOR_START = re.compile(r"(?:^|(?<=/))\^")
_ANCHOR_END = re.compile(r"\$(?=/|$)")


def _normalize(pattern: str) -> str:
    """把 Django 內部的 pattern 字串轉成可讀且穩定的 URL 形式。

    router 產生的是 regex（``^any/getOne/$``），`path()` 產生的是字面字串
    （``basic/login``）。兩者混在同一棵樹裡，直接字串比對會很脆弱。
    """
    result = _ANCHOR_START.sub("", pattern)
    result = _ANCHOR_END.sub("", result)
    return result.replace("\\", "")


def _walk(resolver, prefix=""):
    for entry in resolver.url_patterns:
        if isinstance(entry, URLResolver):
            yield from _walk(entry, prefix + str(entry.pattern))
        else:
            yield prefix + str(entry.pattern), entry


def _class_names(classes):
    if classes is None:
        return None
    return tuple(getattr(c, "__name__", str(c)) for c in classes)


def _resolve_setting(name, initkwargs, view_class, default):
    """依 DRF 的解析順序取得某項設定：@action initkwargs > view class > 全域預設。"""
    if name in initkwargs:
        return _class_names(initkwargs[name])
    if view_class is not None and hasattr(view_class, name):
        return _class_names(getattr(view_class, name))
    return default


def _default_permission_names():
    from rest_framework.settings import api_settings

    return _class_names(api_settings.DEFAULT_PERMISSION_CLASSES)


def _default_authentication_names():
    from rest_framework.settings import api_settings

    return _class_names(api_settings.DEFAULT_AUTHENTICATION_CLASSES)


def collect_routes(include_format_suffixes=False):
    """回傳全部 API 路由，依 `key` 排序。

    :param include_format_suffixes: DefaultRouter 會替每條路由多產生一份
        ``.json`` 格式後綴版本（`^requests\\.(?P<format>[a-z0-9]+)/?$`）。
        那些是同一個 view 的別名，納入只會讓基準檔膨脹一倍，預設排除。
    """
    default_permissions = _default_permission_names()
    default_authentication = _default_authentication_names()

    routes = []
    for raw_path, entry in _walk(get_resolver()):
        path = _normalize(raw_path)
        if any(path.startswith(p) or raw_path.startswith(p) for p in EXCLUDED_PREFIXES):
            continue
        if not include_format_suffixes and (
            "?P<format>" in raw_path or "drf_format_suffix" in raw_path
        ):
            continue

        callback = entry.callback
        view_class = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
        initkwargs = getattr(callback, "initkwargs", None) or {}
        actions = getattr(callback, "actions", None) or {}

        if view_class is not None:
            view_name = f"{view_class.__module__}.{view_class.__name__}"
        else:
            view_name = f"{getattr(callback, '__module__', '?')}.{getattr(callback, '__name__', '?')}"

        routes.append(
            Route(
                path=path,
                methods=tuple(
                    sorted(
                        m
                        for m in {a.upper() for a in actions}
                        if m not in _DERIVED_METHODS
                    )
                ),
                view=view_name,
                permissions=_resolve_setting(
                    "permission_classes", initkwargs, view_class, default_permissions
                )
                or (),
                authentication=_resolve_setting(
                    "authentication_classes", initkwargs, view_class, default_authentication
                )
                or (),
                throttle_scope=initkwargs.get(
                    "throttle_scope", getattr(view_class, "throttle_scope", None)
                ),
            )
        )

    return sorted(routes, key=lambda r: r.key)


def routes_by_key():
    return {r.key: r for r in collect_routes()}
