from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.article.views import ArticleViewSet

# 創建一個Router並註冊ViewSet
router = SimpleRouter()
router.register(r'all', ArticleViewSet, basename='article')

urlpatterns = router.urls