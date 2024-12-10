from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.picture.views import SelfImageViewSet, CompanyImageViewSet, ProductImageViewSet
from apps.picture.slide_views import SlideImageViewSet

router = SimpleRouter()

router.register(r'self-images', SelfImageViewSet, basename='selfimage')
router.register(r'company-images', CompanyImageViewSet, basename='companyimage')
router.register(r'product-images', ProductImageViewSet, basename='productimage')
router.register(r'slide-images', SlideImageViewSet, basename='slideimage')

urlpatterns = router.urls
