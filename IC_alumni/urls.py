"""
URL configuration for IC_alumni project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path ,include

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# JWT
from rest_framework_simplejwt.views import (
    TokenVerifyView,
    TokenBlacklistView,
)

# swagger
schema_view = get_schema_view(
    openapi.Info(
        title="系統開放之API",
        default_version='v1',
        description="系友會會員管理 API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="robin92062574@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(),  # 這裡不需要身份驗證
    #    security=[{'Bearer': []}],  # 添加這一行
)



urlpatterns = [
    path('database/admin/', admin.site.urls),
    # 帳號使用
    path('basic/',include("apps.private.urls")),
    # 系友
    path("member/", include("apps.member.urls")),
    # 系友公司
    path("company/",include("apps.company.urls")),
    # 系友公司產品
    path("product/",include("apps.product.urls")),
    # 招募
    path("recruit/",include('apps.recruit.urls')),
    # 照片管理
    path("picture/",include('apps.picture.urls')),
    # 文章
    path("article/",include('apps.article.urls')),
    # 系友會簡介
    path("info/", include('apps.Info.urls')),

    # API LIST
    path('server/api/swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('server/api/redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# 開啟測試伺服器照片

if settings.DEBUG:
    # 只有在開發模式下使用static.serve視圖
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)