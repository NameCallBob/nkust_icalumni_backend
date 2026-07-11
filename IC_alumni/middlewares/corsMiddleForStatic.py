from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class CORSMiddlewareForStaticFiles(MiddlewareMixin):
    """
    僅針對靜態 / 媒體檔案放寬 CORS。

    [資安修補 MED-2] 原本對「所有」回應都加上 Access-Control-Allow-Origin: *，
    等於讓任何來源都能讀取 API 回應，使 settings 中精心設定的 CORS_ALLOWED_ORIGINS 形同虛設。
    改為僅在 /static/ 與 /media/ 路徑加上寬鬆標頭，API 回應交由 django-cors-headers 控管。
    """
    def process_response(self, request, response):
        path = request.path or ""
        if path.startswith("/static/") or path.startswith("/media/"):
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"
        return response