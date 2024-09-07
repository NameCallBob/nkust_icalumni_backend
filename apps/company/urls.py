from rest_framework.routers import SimpleRouter
from apps.company import views
from django.urls import path

router = SimpleRouter()
router.register(r'data', views.CompanyViewSet,basename="company_dataMaintaince")
# router.register(r'search',views.CompanyListView.as_view,basename="company_search")

urlpatterns = router.urls

urlpatterns += [
    path("search/",views.CompanyListView.as_view())
]