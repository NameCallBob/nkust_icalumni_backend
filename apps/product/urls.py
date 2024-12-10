from rest_framework.routers import SimpleRouter
from apps.product import views
from django.urls import path

router = SimpleRouter()
router.register(r'data', views.ProductViewSet,basename="product_dataMaintaince")
# router.register(r'search',views.ProductListView,basename="product_search")

urlpatterns = router.urls

urlpatterns += [
    path('search/',views.ProductListView.as_view())
]