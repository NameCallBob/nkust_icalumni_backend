from django.urls import path
from apps.private.views import LoginView ,PasswordResetRequestView, PasswordResetConfirmView , MemberRegisterView
from apps.private.private_views import PrivateViewSet , PrivateSearchViewSet
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'private', PrivateViewSet,basename="private")
router.register(r'private_search', PrivateSearchViewSet,basename="privateSear")
urlpatterns = router.urls

urlpatterns += [
    path("login",LoginView.as_view(),name='login'),
    path("forgot_password",PasswordResetRequestView.as_view(),name="password_request"),
    path("forgot_verify",PasswordResetConfirmView.as_view(),name="password_verify"),
    path("register", MemberRegisterView.as_view() , name="member_register_no_active")
]
