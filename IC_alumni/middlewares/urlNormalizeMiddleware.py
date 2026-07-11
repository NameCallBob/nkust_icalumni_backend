from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
import re


class URLNormalizeMiddleware(MiddlewareMixin):
    """
    中間件用於處理URL中的雙斜線問題
    將雙斜線（//）自動重定向為單斜線（/）
    """

    def process_request(self, request):
        # 獲取完整的URL路徑
        path = request.get_full_path()

        # 檢查是否包含雙斜線
        if '//' in path:
            # 將所有雙斜線替換為單斜線，但保留協議後的雙斜線（如 https://）
            normalized_path = re.sub(r'(?<!:)//+', '/', path)

            # 如果路徑發生了變化，進行301重定向
            if normalized_path != path:
                # 構建完整的重定向URL
                scheme = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                redirect_url = f"{scheme}://{host}{normalized_path}"

                return HttpResponsePermanentRedirect(redirect_url)

        return None