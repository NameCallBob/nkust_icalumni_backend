from rest_framework.routers import SimpleRouter
from apps.recruit import views , views_admin
from django.urls import path

router = SimpleRouter()
router.register(r'data', views.RecruitViewSet,basename="recruit")
router.register(r'admin', views_admin.AdminRecruitViewSet, basename='admin-recruit')

urlpatterns = router.urls