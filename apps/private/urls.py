from django.urls import path
from apps.private.views import LoginView ,PasswordResetRequestView, PasswordResetConfirmView , MemberRegisterView

urlpatterns = [
    path("login",LoginView.as_view(),name='login'),
    path("forgot_password",PasswordResetRequestView.as_view(),name="password_request"),
    path("forgot_verify",PasswordResetConfirmView.as_view(),name="password_verify"),
    path("register", MemberRegisterView.as_view() , name="member_register_no_active")
]
