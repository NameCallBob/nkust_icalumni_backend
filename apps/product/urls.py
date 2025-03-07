from rest_framework.routers import SimpleRouter
from apps.product import views
from django.urls import path

router = SimpleRouter()
router.register(r'data', views.ProductViewSet,basename="product_dataMaintaince")
# router.register(r'search',views.ProductListView,basename="product_search")
router.register(r'categories', views.ProductCateViewSet, basename='product-category')

urlpatterns = router.urls
