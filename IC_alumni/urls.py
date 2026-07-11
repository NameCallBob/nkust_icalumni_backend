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

from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

# 公開聯絡我們端點
from apps.record.contact_views import ContactCreateView


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

    path('api/monitoring/', include('apps.record.urls')),

    # 聯絡我們（公開表單，前端 ContactUsPage 使用）
    path('record/contact/', ContactCreateView.as_view(), name='contact_create'),

    # SEO 相關路由
    path('api/seo/', include('apps.seo.urls')),

    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# [資安修補 SEC-020] API schema 文件（Swagger/Redoc）會完整揭露所有端點/參數/資料模型，
# 大幅降低攻擊門檻。改為僅在 DEBUG 或明確設定 EXPOSE_API_DOCS=1 時對外開放。
import os as _os
if settings.DEBUG or _os.getenv("EXPOSE_API_DOCS", "0") == "1":
    urlpatterns += [
        path('server/api/swagger/', schema_view.with_ui('swagger',
             cache_timeout=0), name='schema-swagger-ui'),
        path('server/api/redoc/', schema_view.with_ui('redoc',
             cache_timeout=0), name='schema-redoc'),
    ]

# 靜態檔案和媒體檔案服務（支援DEBUG=False）
if settings.DEBUG:
    # 開發模式下的靜態檔案服務
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # 生產模式下的靜態檔案服務（僅限開發測試用）
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT,
        }),
        re_path(r'^media/+(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

