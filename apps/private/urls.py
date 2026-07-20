from django.urls import path
from apps.private.views import (
    LoginView, PasswordResetRequestView, PasswordResetConfirmView, MemberRegisterView,
    LogoutView, WhoAmIView,
)
from apps.private.private_views import PrivateViewSet , PrivateSearchViewSet
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'private', PrivateViewSet,basename="private")
router.register(r'private_search', PrivateSearchViewSet,basename="privateSear")
urlpatterns = router.urls

urlpatterns += [
    path("login",LoginView.as_view(),name='login'),
    # [資安修補 SEC-015] JWT 改存 HttpOnly cookie 後新增的兩支端點
    path("logout", LogoutView.as_view(), name='logout'),
    path("whoami", WhoAmIView.as_view(), name='whoami'),
    path("forgot_password",PasswordResetRequestView.as_view(),name="password_request"),
    path("forgot_verify",PasswordResetConfirmView.as_view(),name="password_verify"),
    path("register", MemberRegisterView.as_view() , name="member_register_no_active")
]
