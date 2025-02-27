class CurrentRequestMiddleware:
    """
    獲取目前的請求資訊（例如 IP 地址、User-Agent）。
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_ip = self.get_client_ip(request)
        request.user_agent = request.META.get("HTTP_USER_AGENT", "")
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")