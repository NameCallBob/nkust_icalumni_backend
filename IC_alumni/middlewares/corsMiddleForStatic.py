from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class CORSMiddlewareForStaticFiles(MiddlewareMixin):
    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"
        return response