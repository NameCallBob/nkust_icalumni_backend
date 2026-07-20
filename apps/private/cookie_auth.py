"""
Cookie-based JWT authentication（SEC-015 修補）。

原本登入成功後 access token 回在 JSON body，前端存進 localStorage 供 Axios 組
Authorization: Bearer <token> header —— 任何 XSS 都能直接讀 localStorage 冒充身分。
改為登入成功時把 token 寫入 HttpOnly cookie（JS 無法讀取），瀏覽器後續請求自動附帶。
向下相容既有的 Authorization: Bearer <token> header 認證方式（兩者並存，之後可視情況移除 header 分支）。

Cookie 是瀏覽器自動附帶，需額外做 CSRF 驗證；Bearer header 天生不受 CSRF 影響（需要
攻擊者能設定自訂 header 才能偽造，一般表單/圖片式 CSRF 攻擊做不到），所以只在走 cookie
分支時才檢查 CSRF，header 分支維持原樣不受影響。
"""
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class _CSRFCheck(CsrfViewMiddleware):
    """借用 Django CsrfViewMiddleware 的驗證邏輯，但不要它自動產生 HttpResponse——
    process_view 回傳非 None 就代表驗證失敗的原因字串，由呼叫端自行包裝成 DRF 例外。"""

    def _reject(self, request, reason):
        return reason


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None
        else:
            raw_token = request.COOKIES.get(settings.JWT_COOKIE_NAME)
            if raw_token is None:
                return None
            self._enforce_csrf(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def _enforce_csrf(self, request):
        check = _CSRFCheck(get_response=lambda r: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF 驗證失敗：{reason}")
