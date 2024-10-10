from rest_framework.routers import SimpleRouter
from apps.company import views
from django.urls import path

router = SimpleRouter()
router.register(r'data', views.CompanyViewSet,basename="company_dataMaintaince")
router.register(r'industry',views.IndustryViewSet,basename="industry_modify")

urlpatterns = router.urls

urlpatterns += [
    path("search/",views.CompanyListView.as_view())
]