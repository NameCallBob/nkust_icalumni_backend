# monitoring/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.record.views import (RequestLogViewSet, QueryLogViewSet, PopularQueryViewSet,
                    IPLimitViewSet, CRUDLogViewSet, ErrorLogViewSet,
                    PerformanceMetricViewSet)

router = DefaultRouter()
router.register(r'requests', RequestLogViewSet)
router.register(r'queries', QueryLogViewSet)
router.register(r'popular-queries', PopularQueryViewSet)
router.register(r'ip-limits', IPLimitViewSet)
router.register(r'crud-logs', CRUDLogViewSet)
router.register(r'errors', ErrorLogViewSet)
router.register(r'performance', PerformanceMetricViewSet)

app_name = 'monitoring'

urlpatterns = [
    path('', include(router.urls)),
]