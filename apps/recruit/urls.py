from rest_framework.routers import SimpleRouter
from apps.recruit import views
from django.urls import path

router = SimpleRouter()
router.register(r'data', views.RecruitViewSet,basename="recruit")

urlpatterns = router.urls