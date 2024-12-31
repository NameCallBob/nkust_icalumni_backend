from rest_framework.routers import SimpleRouter
from apps.record import views
from django.urls import path

router = SimpleRouter()
router.register(r'contact', views.ContactForm,basename="contact")

urlpatterns = router.urls
